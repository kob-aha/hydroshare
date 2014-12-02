import factory
from django.core.files import File



class Bags(factory.DjangoModelFactory):
    class Meta:
        model = 'hs_core.Bags'


class ResourceFile(factory.DjangoModelFactory):
    class Meta:
        model = 'hs_core.ResourceFile'


class GenericResource(factory.DjangoModelFactory):
    bags = factory.RelatedFactory(Bags)
    files = factory.RelatedFactory(ResourceFile)

    class Meta:
        model = 'hs_core.GenericResource'
        django_get_or_create = 'slug'


class RichTextPageFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'pages.RichTextPage'

class HomePageFactory(factory.DjangoModelFactory):
    title='Home'
    slug='/'
    heading='Hydroshare'
    header_image=factory.LazyAttribute(lambda a: 'background.jpg')
    header_background=factory.LazyAttribute(lambda a: 'background.jpg')
    welcome_heading='Share and Collaborate'
    content='Hydroshare is an online collaboration environment for sharing data, models, and code.  Join the community to start sharing.'
    recent_blog_heading='Latest blog posts'
    number_recent_posts=3
    in_menus=[]
    
    class Meta:
        model = 'theme.HomePage'


def create_initial_pages():
    """Create a set of pages that every Hydroshare instance needs"""
    RichTextPageFactory.create(
        title='Resources',
        slug='my-resources',
        content='a'
    )

    RichTextPageFactory.create(
        title='Support',
        slug='help',
        content='a'
    )

    RichTextPageFactory.create(
        title='Create Resource',
        slug='create-resource',
        content='a'
    )

    RichTextPageFactory.create(
        title='Terms of Use',
        content=open('terms-of-use.html').read())

    RichTextPageFactory.create(
        title='Privacy',
        content=open('privacy.html').read())
    
    HomePageFactory.create()

