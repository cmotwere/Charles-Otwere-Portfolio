import shutil
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from .models import (
    About, BlogPost, Certification, DownloadTracking, Education, Event,
    Project, Skill,
)


class PortfolioDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.about = About.objects.create(name='Test Person', bio='Bio', email='me@example.com')
        cls.skill = Skill.objects.create(name='Python', category='programming', proficiency='expert')
        cls.project = Project.objects.create(
            title='Demo', slug='demo', short_description='Short', description='Long',
            project_type=Project.PROJECT_TYPES[0][0], start_date=date(2025, 1, 1),
        )
        cls.project.technologies_used.add(cls.skill)
        cls.post = BlogPost.objects.create(title='Published post', content='Body', status='published')
        cls.draft = BlogPost.objects.create(title='Secret draft', content='WIP', status='draft')
        cls.event = Event.objects.create(title='Meetup', slug='meetup', date=date(2025, 5, 1))
        cls.staff = User.objects.create_user('staff', password='pw-123456!', is_staff=True)


class PublicPagesTests(PortfolioDataMixin, TestCase):
    def test_public_pages_load(self):
        urls = [
            '/', '/about/', '/projects/', '/projects/demo/', '/skills/', '/contact/',
            '/privacy-policy/', '/testimonials/', '/education/', '/certifications/',
            '/experience/', '/blog/', f'/blog/post/{self.post.slug}/', '/events/',
            '/events/meetup/', '/portfolio/', '/manifest.json', '/sw.js',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_removed_endpoints_are_gone(self):
        for url in ['/auth/login/', '/auth/register/', '/api/projects/', '/api/v1/projects/',
                    '/api/contact/', '/blog/debug/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_search_box_is_empty_without_query(self):
        self.assertNotContains(self.client.get('/projects/'), 'value="None"')

    def test_page_title_uses_name_from_admin(self):
        self.assertContains(self.client.get('/projects/'), '<title>Projects - Test Person</title>')

    def test_blog_post_meta_description(self):
        BlogPost.objects.filter(pk=self.post.pk).update(meta_description='Custom SEO text')
        self.assertContains(self.client.get(f'/blog/post/{self.post.slug}/'),
                            'name="description" content="Custom SEO text"')

    def test_project_list_queries_do_not_grow_per_project(self):
        for i in range(5):
            p = Project.objects.create(
                title=f'P{i}', slug=f'p{i}', short_description='s', description='d',
                project_type=Project.PROJECT_TYPES[0][0], start_date=date(2025, 1, 1),
            )
            p.technologies_used.add(self.skill)
        self.client.get('/projects/')  # warm up sessions/context processors
        # about (context processor) + projects + one prefetch for all technologies
        with self.assertNumQueries(3):
            self.client.get('/projects/')


class DraftVisibilityTests(PortfolioDataMixin, TestCase):
    def test_drafts_hidden_from_public(self):
        self.assertEqual(self.client.get(f'/blog/post/{self.draft.slug}/').status_code, 404)
        self.assertNotContains(self.client.get('/blog/?debug=true'), 'Secret draft')

    def test_staff_can_preview_drafts(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(f'/blog/post/{self.draft.slug}/').status_code, 200)
        self.assertContains(self.client.get('/blog/?debug=true'), 'Secret draft')


class DownloadTests(TestCase):
    def setUp(self):
        self.media = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.media)
        (self.media / 'resume').mkdir()
        (self.media / 'resume' / 'CV.pdf').write_bytes(b'%PDF-test')
        (self.media / 'secret.env').write_text('SECRET=1')
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)

    def test_resume_downloads_and_is_tracked(self):
        response = self.client.get('/download/resume/CV.pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'%PDF-test')
        self.assertEqual(DownloadTracking.objects.count(), 1)

    def test_path_traversal_is_refused(self):
        for url in ['/download/%2e%2e/secret.env/', '/download/resume/%2e%2e/',
                    '/download/resume/.env/', '/download/about/x.png/',
                    '/download/resume/missing.pdf/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(DownloadTracking.objects.count(), 0)

    def test_resume_link_renders_when_resume_uploaded(self):
        About.objects.create(name='A', bio='b', email='a@example.com', resume_file='resume/CV.pdf')
        self.assertContains(self.client.get('/'), '/download/resume/CV.pdf/')


class DisplayTests(TestCase):
    def test_skills_sorted_by_proficiency_level(self):
        for level in ['intermediate', 'beginner', 'expert', 'advanced']:
            Skill.objects.create(name=level, category='programming', proficiency=level)
        self.assertEqual(
            list(Skill.objects.values_list('proficiency', flat=True)),
            ['expert', 'advanced', 'intermediate', 'beginner'],
        )

    def test_all_certifications_listed(self):
        Certification.objects.create(name='Expired cert', issuing_organization='Org',
                                     issue_date=date(2020, 1, 1), status='expired')
        Certification.objects.create(name='Ongoing cert', issuing_organization='Org',
                                     issue_date=date(2025, 1, 1), status='in_progress')
        response = self.client.get('/certifications/')
        self.assertContains(response, 'Expired cert')
        self.assertContains(response, 'Ongoing cert')

    def test_expiring_soon_uses_30_days(self):
        today = date.today()
        Certification.objects.create(name='Soon', issuing_organization='Org', status='active',
                                     issue_date=date(2024, 1, 1), expiry_date=today + timedelta(days=10))
        Certification.objects.create(name='Later', issuing_organization='Org', status='active',
                                     issue_date=date(2024, 1, 1), expiry_date=today + timedelta(days=45))
        expiring = list(self.client.get('/certifications/').context['expiring_certs'])
        self.assertEqual([c.name for c in expiring], ['Soon'])

    def test_in_progress_education_gets_amber_badge(self):
        Education.objects.create(institution='Uni', degree_type=Education.DEGREE_TYPES[0][0],
                                 program_name='MSc', start_date=date(2025, 1, 1), status='in_progress')
        self.assertContains(self.client.get('/education/'), 'mbadge-amber')


class ContactSpamTests(TestCase):
    def _post(self, **extra):
        data = {'name': 'N', 'email': 'n@example.com', 'subject': 'S', 'message': 'M',
                'form_ts': str(time.time() - 60)}
        data.update(extra)
        return self.client.post('/contact/', data)

    @mock.patch('portfolio.views.send_mail')
    def test_honeypot_submission_is_dropped(self, send_mail):
        self._post(hp_url='http://spam.example')
        send_mail.assert_not_called()

    @mock.patch('portfolio.views.send_mail')
    def test_instant_submission_is_dropped(self, send_mail):
        self._post(form_ts=str(time.time()))
        send_mail.assert_not_called()

    @override_settings(TURNSTILE_SITE_KEY='site', TURNSTILE_SECRET_KEY='')
    @mock.patch('portfolio.views.send_mail')
    def test_missing_turnstile_secret_fails_closed(self, send_mail):
        self._post()
        send_mail.assert_not_called()
