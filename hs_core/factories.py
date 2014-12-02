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


def create_initial_data(*args, **kwargs):
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

    RichTextPageFactory.create(
        title='Verify Account',
        content="""
<p>Thank you for signing up for HydroShare! We have sent you an email from hydroshare.org to verify your account. &nbsp;Please click on the link within the email and verify your account with us and you can get started sharing data and models with HydroShare.</p>
<p><a href="/hsapi/_internal/resend_verification_email/">Please click here if you do not receive a verification email within 1 hour.</a></p>""",
       
    
    HomePageFactory.create()


def create_test_resources(*args, **kwargs):
    """
    all apps that define new hydroshare resource types should define this 
    function.  Each app that defines this function in its factories.py will 
    create a set of resources for testing purposes when the user executes 
    python manage.py create_test_resources
    """
    print "No resources to define"
