# Create your views here.

#from django.conf.urls.defaults import *
#from django.shortcuts import render_to_response, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect

# 2016-02-26 KWS Required for authentication
from django.contrib import auth
from django.template.context_processors import csrf
#from django.template.context_processors import csrf

from django.urls import reverse
from django.db.models import Avg, Max, Min, Count
from django.db import IntegrityError
from atlas.models import TcsPostageStampImages
from atlas.models import TcsClassificationFlags
from atlas.models import TcsDetectionLists
from atlas.models import TcsCrossMatches
from atlas.models import TcsCrossMatchesExternal
from atlas.models import TcsObjectGroups
from atlas.models import TcsObjectGroupDefinitions
from atlas.models import TcsProcessingStatus
from atlas.models import AtlasDiffObjects
from atlas.models import AtlasDiffDetections
from atlas.models import AtlasDetectionsddc
from atlas.models import TcsPostageStampImages
from atlas.models import TcsLatestObjectStats
from atlas.models import AtlasForcedPhotometry
from atlas.models import TcsImages
# 2017-03-21 KWS Added TcsGravityEventAnnotations, SherlockClassifications
from atlas.models import TcsGravityEventAnnotations
from atlas.models import SherlockClassifications
from atlas.models import SherlockCrossmatches
from atlas.models import TcsObjectComments
# 2019-06-06 KWS Get the new diff stack forced photometry data
from atlas.models import AtlasStackedForcedPhotometry
from atlas.dbviews import *
# import django_tables as tables
from math import log, sqrt
import datetime

from django import forms

# Required for pagination
from django.template import RequestContext

# base 26 numbers for candidate names
from gkutils.commonutils import base26, ra_to_sex, dec_to_sex, ra_in_decimal_hours, coneSearchHTM, QUICK, FULL, COUNT, CAT_ID_RA_DEC_COLS, FLAGS, getFlagDefs, transform, J2000toGalactic, getDateFractionMJD, COORDS_SEX_REGEX_COMPILED, COORDS_DEC_REGEX_COMPILED, NAME_REGEX_COMPILED, calculateRMSScatter, dbConnect, Struct
from atlas.helpers import processSearchForm, getNearbyObjectsFromAlternateDatabase, sendMessage, TNS_MESSAGES, getNearbyObjectsForScatterPlot, SHOW_LC_DATA_LIMIT, filterGetParameters, filterGetGWParameters, getDjangoTables2ImageTemplate

# *** FGSS CODE ***
#from catalogueviews import *

# 2011-02-24 KWS Moved all the form choices into a separate file
from atlas.formchoices import *

from django.db.models import Q    # Need Q objects for OR query

# Does an object exist?
from django.core.exceptions import ObjectDoesNotExist

# We need to know which database we are talking to for the lightcurves.
from django.conf import settings

# 2012-07-18 KWS Moved all raw lightcurve queries to a dedicated file
from .lightcurvequeries import *

# 2013-02-05 KWS Moved raw lightcurve queries again to a common queries
#                file that can be called by both scripts and Django code.
from .commonqueries import lightcurvePlainQuery, colourDataPlainQuery, FOLLOWUP_LIST_QUERY, FILTERS

# 2015-11-30 KWS Dependencies for Django Tables 2
from django_tables2 import RequestConfig
from django_tables2.utils import A  # alias for Accessor
import django_tables2 as tables2

# 2016-02-09 KWS Attempt to paginate raw query with django-sqlpaginator
#from sqlpaginator.paginator import SqlPaginator
#from atlas.sqlpaginator import SqlPaginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# 2016-02-26 KWS Required for authentication
from django.contrib.auth.decorators import login_required

# 2022-05-06 KWS New model - AtlasDiffSubcells
from atlas.models import AtlasDiffSubcells

# 2022-09-06 KWS New model - AtlasHeatmaps
from atlas.models import AtlasHeatmaps

from django.http import Http404

# 2022-11-16 KWS If the Lasair API is unreachable we should catch the connection error.
# 2023-01-03 KWS If the Lasair API times out we should catch the timeout error.
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout as RequestsConnectionTimeoutError

# 2023-01-06 KWS Import the new code to grab a name from the nameserver.
#                Requires an update to gkutils.
from gkutils.commonutils import getLocalObjectName


class LoginForm(forms.Form):
    """LoginForm.
    """

    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'50', 'class':'form-control'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'size':'50', 'class':'form-control'}))

def login(request):
    """login.

    Args:
        request:
    """
    auth.logout(request)
    username = password = ''
    form = LoginForm()
    return render(request, 'login.html', {'form': form})


def authView(request):
    """authView.

    Args:
        request:
    """
    # Although we picked up the "next" parameter via GET in our template,
    # we submitted it via POST.
    next = request.POST.get('next', '')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        # Expire the login session after 1 day.
        # 2017-11-28 KWS Changed expiry to 30 days. 1 day expiry too irritating.
        request.session.set_expiry(30 * 86400)
        auth.login(request, user)
        if next == '':
            return redirect('home')
        else:
            return redirect(next)

    else:
        return redirect('invalid')

def loggedin(request):
    """loggedin.

    Args:
        request:
    """
    return render(request, 'loggedin.html',
                              {'full_name': request.user.username})

def invalidLogin(request):
    """invalidLogin.

    Args:
        request:
    """
    return render(request, 'invalid_login.html')

def logout(request):
    """logout.

    Args:
        request:
    """
    auth.logout(request)
    return render(request, 'logout.html')

def csrf_failure(request, reason=""):
    """csrf_failure.

    Args:
        request:
        reason:
    """
    return render(request, 'invalid_login.html', {'message': 'CSRF failure'})



class TcsDetectionListsForm(forms.Form):
    """TcsDetectionListsForm.
    """

    name = forms.CharField()

GARBAGE, FOLLOWUP, GOOD, POSSIBLE, EYEBALL, ATTIC, STAR, AGN, FASTEYE, MOVERS, SMCLMC, HPMSTAR = list(range(12))

OBJECT_LISTS = {
    'Garbage': GARBAGE,
    'Followup': FOLLOWUP,
    'Good': GOOD,
    'Possible': POSSIBLE,
    'Eyeball': EYEBALL,
    'Attic': ATTIC,
    'Star': STAR,
    'AGN': AGN,
    'FastEye': FASTEYE,
    'Movers': MOVERS,
    'SMCLMC': SMCLMC,
    'HPMStar': HPMSTAR,
    'DoNothing': -1
}

SURVEY_FIELDS = {
    'ATLAS': 'ATLAS',
    'RINGS': '3P',
    'FGSS': '3F',
    'MD01': '01',
    'MD02': '02',
    'MD03': '03',
    'MD04': '04',
    'MD05': '05',
    'MD06': '06',
    'MD07': '07',
    'MD08': '08',
    'MD09': '09',
    'MD10': '10',
    'M31': '31',
}

MONTHS = 'ABCDEFGHIJKL'

ALTERNATE_DB_CONNECTIONS = {'ps1md': ['ps1ss', 'psdb', 'http://star.pst.qub.ac.uk/ps1/psdb/'],
                      'ps1fgss': ['ps1fgssold', 'psdb', 'http://star.pst.qub.ac.uk/ps1fgss/psdb/'],
                      'ps1fgssold': ['ps1fgss', 'psdb2', 'https://star.pst.qub.ac.uk/sne/ps1fgss/psdb/'],
                      'ps1kws': ['ps1ss', 'psdb', 'https://star.pst.qub.ac.uk/ps1/psdb/'],
                      'ps1ss': ['ps1md', 'psdb2', 'https://star.pst.qub.ac.uk/sne/ps1md/psdb/'],
                      'ps1gw': ['ps13pi', 'psdb2', 'https://star.pst.qub.ac.uk/sne/ps13pi/psdb/'],
                      'atlas3': ['atlas4', 'db1', 'https://star.pst.qub.ac.uk/sne/atlas4/'],
                      'atlas4': ['atlas3', 'db4', 'https://star.pst.qub.ac.uk/sne/atlas3/'],
                      'ps13pi': ['ps1md', 'psdb2', 'https://star.pst.qub.ac.uk/sne/ps1md/psdb/']}

# 2013-09-25 KWS Added lightcurve limits which are dependent on database (default is Medium Deep)
# 2014-07-03 KWS Added new filters, w and x, and also B and V for ATLAS.

LC_LIMITS_MD = {"g": 23.6,
                "r": 23.6,
                "i": 23.6,
                "z": 22.6,
                "y": 21.3,
                "w": 23.6,
                "x": 21.3}

# Refer to Inserra et al for detail of these limits. The limits below
# are in fact set to 1 mag shallower than in Inserra's paper.
# (Inserra et al. 2013, ApJ, 770, 128)
#LC_LIMITS_3PI = {"g": 22.0,
#                 "r": 21.7,
#                 "i": 21.7,
#                 "z": 21.4,
#                 "y": 19.3}

# 2015-02-26 KWS Set the w-band limit to 22.0 for the time being until
#                a formal analysis is done.
LC_LIMITS_3PI = {"g": 21.0,
                 "r": 20.6,
                 "i": 20.7,
                 "z": 20.4,
                 "y": 18.3,
                 "w": 22.0,
                 "x": 19.5}

LC_LIMITS_ATLAS = {"g": 20.5,
                   "r": 20.5,
                   "i": 20.5,
                   "z": 20.5,
                   "y": 20.5,
                   "w": 20.5,
                   "x": 20.5,
                   "B": 20.5,
                   "V": 20.5,
                   "R": 20.5,
                   "I": 20.5,
                   "c": 20.5,
                   "o": 20.5,
                   "h": 20.5}

LC_LIMITS = {'ps1md': LC_LIMITS_MD,
            'ps1ss': LC_LIMITS_MD,
            'ps1kws': LC_LIMITS_MD,
            'ps1fgss': LC_LIMITS_3PI,
            'ps13pi': LC_LIMITS_3PI, 
            'ps13pipublic': LC_LIMITS_3PI,
            'atlas': LC_LIMITS_ATLAS }




# 2011-02-24 KWS Added drop-down list for observation status
# 2011-04-04 KWS Added drop-down list for User Defined List - populated from the database
class PromoteAndCommentsForm(forms.Form):
    """PromoteAndCommentsForm.
    """

    observation_status = forms.ChoiceField(required=False, label='Spectral Type', widget=forms.Select(attrs={'class':'form-control'}), choices=OBSERVATION_STATUS_CHOICES)
    comments = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'80','class':'form-control','placeholder':'Comment','maxlength':'256'}))
    promote_demote = forms.ChoiceField(label='', widget=forms.RadioSelect(attrs={'autocomplete':'off'}), choices=PROMOTION_CHOICES)
    list_add = forms.ChoiceField(required=False, label='Add to List', widget=forms.Select(attrs={'class':'form-control'}), choices=())

    # 2011-04-13 KWS Add a hidden field to capture the page where we came from.
    user_list_membership = forms.MultipleChoiceField(label='Remove From List', widget=forms.CheckboxSelectMultiple, choices=(), required=False)

    # 2011-04-13 KWS Add a hidden field to capture the page where we came from.
    redirect_url = forms.CharField(widget=forms.HiddenInput, required=False)

    # Populate the list add field and remove field with the choices in the database
    def __init__(self, *args, **kwargs):
        """__init__.

        Args:
            args:
            kwargs:
        """
        super(PromoteAndCommentsForm, self).__init__(*args, **kwargs)
        listChoices = [(lc.id, lc.description) for lc in TcsObjectGroupDefinitions.objects.all()]
        self.fields['user_list_membership'].choices = listChoices
        # Add a null list to the user defined lists (for display purposes only)
        listChoices.append(('0', 'None'))
        self.fields['list_add'].choices = listChoices


# 2011-03-16 KWS Object search form
class SearchForObjectForm(forms.Form):
    """SearchForObjectForm.
    """

    searchText = forms.CharField(required=True, widget=forms.TextInput(attrs={'size':'20'}))
 
    # 2016-08-26 KWS Override clean method to check for:
    #                * Up to 4 lowercase letters (check IAU and ATLAS names)
    #                * Starts with number from 15 upwards (check IAU and ATLAS names)
    #                * ATLAS prefix alone (fail)
    #                * If all above fails try and regex into RA Dec or RA Dec Radius
    #                  in decimal or sexagesimal (with any delimiter)

    def clean_searchText(self):
        """clean_searchText.
        """
        searchString = self.cleaned_data['searchText']

        # Regex test - name, then decimal degrees, then sexagesimal
        if not (NAME_REGEX_COMPILED.search(searchString) or COORDS_SEX_REGEX_COMPILED.search(searchString) or COORDS_DEC_REGEX_COMPILED.search(searchString)):
            raise forms.ValidationError("invalid name or coordinates")
        return searchString



class UserDefinedListDefinitionsTable(tables2.Table):
    """UserDefinedListDefinitionsTable.
    """

    # We want to render the id link as a drop down menu. Do is this way!
    MENU = '''
        <a class="dropdown-toggle" href="#" data-toggle="dropdown">{{ record.id }}</a>
        <div class="dropdown-menu">
        <a class="dropdown-item" href="{% url 'userdefinedlistsquickview' record.id %}">quick view</a>
        <a class="dropdown-item" href="{% url 'userdefinedlists' record.id %}">table view</a>
        </div>
    '''

    id = tables2.TemplateColumn(MENU)
    name = tables2.Column(accessor="name", visible=False)
    description = tables2.Column(accessor="description")

    # OK - the way to add the buttons is to SUBCLASS this table I think
    # adding the relevant buttons depending on the list ID.

    class Meta:
        """Meta.
        """

        model = TcsObjectGroupDefinitions
        template_name = "bootstrap4_django_tables2_atlas.html"


@login_required
def userDefinedListDefinitions(request):
    """userDefinedListDefinitions.

    Args:
        request:
    """
    userListDefinitionsQuery = TcsObjectGroupDefinitions.objects.all()
    table = UserDefinedListDefinitionsTable(userListDefinitionsQuery, order_by=request.GET.get('sort', 'id'))
    RequestConfig(request, paginate={"per_page": 20}).configure(table)
    formSearchObject = SearchForObjectForm()
    return render(request, 'atlas/userdefinedlists_bs.html', {'table': table, 'form_searchobject': formSearchObject})

class WebViewUserDefinedTable(tables2.Table):
    """WebViewUserDefinedTable.
    """

    idtxt = tables2.Column(accessor='id', visible=False)
    id = tables2.LinkColumn('candidate', args=[A('id')])
    atlas_designation = tables2.Column(default='')
    other_designation = tables2.Column(default='')
    local_comments = tables2.Column(default='', visible=False)
    ra = tables2.Column()
    dec = tables2.Column()
    ra_avg = tables2.Column(visible=False)
    dec_avg = tables2.Column(visible=False)
    observation_status = tables2.Column(verbose_name="Spectral Type")
    object_classification = tables2.Column(visible=False, verbose_name="Machine Classification")
    sherlockClassification = tables2.Column(verbose_name="Context Classification")
    catalogue = tables2.Column(visible=False)
    catalogue_object_id = tables2.Column(visible=False, verbose_name="Nearest Object")
    followup_flag_date = tables2.Column(verbose_name="Flag Date")
    separation = tables2.Column(visible=False, verbose_name="Separation (arcsec)")
    object_group_id = tables2.Column(visible=False)
    detection_list_id = tables2.Column(accessor='detection_list_id.name', verbose_name="List")
    realbogus_factor = tables2.Column(verbose_name="RB Factor")
    rb_pix = tables2.Column(verbose_name="RB Factor 2")
    date_modified = tables2.Column(visible=False)
    external_crossmatches = tables2.Column(verbose_name="External Crossmatches")
    discovery_target = tables2.Column(visible=False)
    earliest_mjd_date = tables2.Column(accessor='earliest_mjd', visible=False)
    latest_mjd_date = tables2.Column(accessor='latest_mjd', visible=False)

    def render_ra(self, value, record):
        """render_ra.

        Args:
            value:
            record:
        """
        if record.ra_avg:
            ra_in_sex = ra_to_sex (record.ra_avg)
        else:
            ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec(self, value, record):
        """render_dec.

        Args:
            value:
            record:
        """
        if record.dec_avg:
            dec_in_sex = dec_to_sex (record.dec_avg)
        else:
            dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    def render_ra_avg(self, value):
        """render_ra_avg.

        Args:
            value:
        """
        ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec_avg(self, value):
        """render_dec_avg.

        Args:
            value:
        """
        dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    def render_object_classification(self, value):
        """render_object_classification.

        Args:
            value:
        """
        object_definition = getFlagDefs(value, FLAGS, delimiter = ' ')
        return object_definition

    def render_realbogus_factor(self, value):
        """render_realbogus_factor.

        Args:
            value:
        """
        return '%.3f' % value

    def render_rb_pix(self, value):
        """render_rb_pix.

        Args:
            value:
        """
        return '%.3f' % value

    def render_separation(self, value):
        """render_separation.

        Args:
            value:
        """
        return '%.2f' % value

    def render_earliest_mjd(self, value):
        """render_earliest_mjd.

        Args:
            value:
        """
        return '%.5f' % value

    def render_earliest_mjd_date(self, value):
        """render_earliest_mjd_date.

        Args:
            value:
        """
        dateFraction = getDateFractionMJD(value, delimiter = '')
        return dateFraction

    def render_latest_mjd(self, value):
        """render_latest_mjd.

        Args:
            value:
        """
        return '%.5f' % value

    def render_latest_mjd_date(self, value):
        """render_latest_mjd_date.

        Args:
            value:
        """
        dateFraction = getDateFractionMJD(value, delimiter = '-')
        return dateFraction

    def render_other_designation(self, value, record):
        """render_other_designation.

        Args:
            value:
            record:
        """
        prefix = 'AT'
        if record.observation_status and ('SN' in record.observation_status or 'I' in record.observation_status):
            prefix = 'SN'
        return prefix + value

    class Meta:
        """Meta.
        """

        model = WebViewAbstractUserDefined
        #attrs = {'class': 'followuplists_standardview'}
        template_name = "bootstrap4_django_tables2_atlas.html"

@login_required
def userDefinedLists(request, userDefinedListNumber):
    """userDefinedLists.

    Args:
        request:
        userDefinedListNumber:
    """

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description
    form = SearchForObjectForm()

    if request.method == 'POST':
        form = SearchForObjectForm(request.POST)
        if form.is_valid(): # All validation rules pass
            # Do stuff here

            objectName = form.cleaned_data['searchText']
            if len(objectName) > 0 and objectName != '%%':
                # 2013-07-23 KWS Altered query to extract the relevant IDs from the tcs_transient_objects table
                #                in the hope that this will speed up the query.
                transients_queryset = AtlasDiffObjects.objects.filter(Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName))
                initial_queryset = WebViewFollowupTransients.objects.filter(pk__in=transients_queryset.values_list('id'))
            else:
                initial_queryset = WebViewFollowupTransients.objects.all()
            table = WebViewFollowupTransientsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))

    else:
        form = SearchForObjectForm()
        initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
        table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))

    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": 100}).configure(table)

    return render(request, 'atlas/followup_bs.html', {'table': table, 'rows' : table.rows, 'listHeader' : listHeader, 'form_searchobject': form})


# 2023-06-09 KWS Get GCN formatted user defined lists
@login_required
def gcn(request, userDefinedListNumber, template_name):
    """Create a text only GCN list from a custom list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)

    listHeader = userDefinedListRow.description

    # 2023-06-13 KWS Add ability to filter on a GW event (in case associated with multiple events).
    queryFilterGW = filterGetGWParameters(request, {})

    initial_queryset = TcsObjectGroups.objects.filter(object_group_id = userDefinedListNumber)

    # Grab any GW annotations for any object. What if we have more than one?
    for row in initial_queryset:
        if queryFilterGW:
            g = TcsGravityEventAnnotations.objects.filter(transient_object_id__id = row.transient_object_id.id).filter(**queryFilterGW)
        else:
            g = TcsGravityEventAnnotations.objects.filter(transient_object_id__id = row.transient_object_id.id)
        row.events = g

    return render(request, 'atlas/' + template_name ,{'table': initial_queryset, 'listHeader' : listHeader}, content_type="text/plain")


class AtlasDiffDetectionsTable(tables2.Table):
    """AtlasDiffDetectionsTable.
    """

    mjd = tables2.Column(accessor='atlas_metadata_id.mjd_obs')
    expname = tables2.Column(accessor='atlas_metadata_id.expname')
    mag5sig = tables2.Column(accessor='atlas_metadata_id.mag5sig')
    zp = tables2.Column(accessor='atlas_metadata_id.zp')
    exptime = tables2.Column(accessor='atlas_metadata_id.exptime')
    filter = tables2.Column(accessor='atlas_metadata_id.filter')
    object = tables2.Column(accessor='atlas_metadata_id.object')
    fpra = tables2.Column(accessor='atlas_metadata_id.ra', verbose_name='fpRA')
    fpdec = tables2.Column(accessor='atlas_metadata_id.dec', verbose_name='fpDec')
    class Meta:
        """Meta.
        """

        model = AtlasDiffDetections
        exclude = ['id', 'atlas_metadata_id', 'atlas_object_id', 'htm16id', 'jtindex', 'realbogus_factor', 'date_inserted', 'date_modified', 'quality_threshold_pass', 'deprecated', 'peakval', 'skyval', 'peakfit', 'dpeak', 'skyfit', 'flux', 'dflux', 'major', 'minor', 'phi', 'err']


class AtlasDetectionsddcTable(tables2.Table):
    """AtlasDetectionsddcTable.
    """

    mjd = tables2.Column(accessor='atlas_metadata_id.mjd')
    #obs = tables2.Column(accessor='atlas_metadata_id.obs')
    #obs = tables2.LinkColumn('heatmap', accessor='atlas_metadata_id.obs', args=[A('atlas_metadata_id.obs')])

    obs = tables2.TemplateColumn('''<a href="{% url 'heatmap' record.atlas_metadata_id.obs %}?x={{ record.x }}&y={{ record.y }}">{{ record.atlas_metadata_id.obs }}</a> (<a href="{% url 'heatmap' record.atlas_metadata_id.obs|slice:"0:3" %}?x={{ record.x }}&y={{ record.y }}">{{ record.atlas_metadata_id.obs|slice:"0:3" }}</a>)''')

    mag5sig = tables2.Column(accessor='atlas_metadata_id.mag5sig')
    magzp = tables2.Column(accessor='atlas_metadata_id.magzp')
    texp = tables2.Column(accessor='atlas_metadata_id.texp')
    filt = tables2.Column(accessor='atlas_metadata_id.filt')
    obj = tables2.Column(accessor='atlas_metadata_id.obj')
    fpra = tables2.Column(accessor='atlas_metadata_id.ra', verbose_name='fpRA')
    fpdec = tables2.Column(accessor='atlas_metadata_id.dec', verbose_name='fpDec')
    class Meta:
        """Meta.
        """

        model = AtlasDetectionsddc
        exclude = ['id', 'atlas_metadata_id', 'atlas_object_id', 'htm16id', 'realbogus_factor', 'date_inserted', 'date_modified', 'quality_threshold_pass', 'deprecated']
        template_name = "bootstrap4_django_tables2_atlas.html"

# Experimental code - Use of forms
@login_required
def candidate(request, atlas_diff_objects_id):
    """candidate.

    Args:
        request:
        atlas_diff_objects_id:
    """
    from django.db import connection

    transient = get_object_or_404(AtlasDiffObjects, pk=atlas_diff_objects_id)

    # 2015-11-17 KWS Get the processing status. If it's not 2, what is it?
    processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
    processingStatus = None
    processingStartTime = None
    if len(processingStatusData) == 1:
        processingStatus = processingStatusData[0].status
        processingStartTime = processingStatusData[0].started

    # 2017-03-21 KWS Get Gravity Wave annotations and Sherlock Classifications
    sc = SherlockClassifications.objects.filter(transient_object_id_id = transient.id)
    gw = TcsGravityEventAnnotations.objects.filter(transient_object_id_id = transient.id).filter(enclosing_contour__lt=100)
    existingComments = TcsObjectComments.objects.filter(transient_object_id = transient.id).order_by('date_inserted')

    # 2013-10-30 KWS Get external crossmatches if they exist
    externalXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id = transient.id).order_by('external_designation')

    # 2014-03-11 KWS Pick up any Finder images.
    finderImages = TcsPostageStampImages.objects.filter(image_filename__istartswith = str(transient.id), image_type__iendswith = 'finder')

    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    # 2013-12-12 KWS Is this a PUBLIC database?
    public = False
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    try:
        detectionLimits = LC_LIMITS[dbName]
    except KeyError as e:
        # Default detections limits for medium deep
        detectionLimits = LC_LIMITS_MD

    lcPoints, lcBlanks, plotLabels, lcLimits = getLCData(transient.id, limits = detectionLimits, conn = connection)


    # 2017-10-02 KWS Since we have started a new database we need to crossmatch the old one.
    #                Have we seen the object before?  And does it have a name??
    coneSearchRadius = 3.6

    xmresults = getNearbyObjectsFromAlternateDatabase(dbName, ALTERNATE_DB_CONNECTIONS, transient, coneSearchRadius)


    # 2016-08-11 KWS Get the Forced Photometry data.  We need to completely rethink how this is queried.
    #                In the past I built custom queries that could be called by scripts or web.  Let's
    #                try just building the query using the ORM.

    forcedPhotometry = AtlasForcedPhotometry.objects.filter(atlas_object_id = transient.id).order_by('mjd_obs')

    # 2016-10-16 KWS Just occasionally the forced photometry will NOT produce
    #                a single point on the lightcurve. In this case we should
    #                skip the forced photometry plot.  (In futre, we probably
    #                want to plot the non-detections.
    lcDataForced = []
    if forcedPhotometry:
        nonLimitingMagsExist = False
        for row in forcedPhotometry:
            if not row.limiting_mag:
                nonLimitingMagsExist = True
                break
        if nonLimitingMagsExist:
            forcedDetectionData, forcedDetectionDataBlanks, forcedPlotLabels, forcedPlotLimits = organiseAtlasForcedPhotometryForPlotting(forcedPhotometry)
            lcDataForced = [forcedDetectionData, forcedDetectionDataBlanks, forcedPlotLabels, forcedPlotLimits]

    # Get the recurrence data. With the ATLAS schema, we already have all the detections in one place.
    # Note that we should probably aggregate this code together into a function.

    detections = AtlasDiffDetections.objects.filter(atlas_object_id = transient.id).filter(deprecated__isnull = True)
    table = AtlasDiffDetectionsTable(detections)
    #RequestConfig(request, paginate={"per_page": 1}).configure(table)
    RequestConfig(request, paginate=False).configure(table)

    # Convert the detections to a format understandable by the rms calculator.
    recurrences = []
    footprints = []
    for row in detections:
        recurrences.append({"RA": row.ra, "DEC": row.dec})
        footprints.append({"RA": row.atlas_metadata_id.ra, "DEC": row.atlas_metadata_id.dec, "footprintName": row.atlas_metadata_id.object})

    distinctFootprints = set([f['footprintName'] for f in footprints])

    fpData = {}

    if len(distinctFootprints) == 1:
        # We have exactly one footprint
        # Use the average RA and Dec as the input RA and Dec (where the origin will be plotted)
        # (Yes - I know - we are doing this calculation twice!)
        avgRa, avgDec, rms = calculateRMSScatter(footprints)
        fprecurrencePlotData, fprecurrencePlotLabels, fpaverageObjectCoords, fprmsScatter = getRecurrenceDataForPlotting(footprints, avgRa, avgDec, objectColour = 21)
        fpData['plotdata'] = fprecurrencePlotData
        fpData['plotlabels'] = fprecurrencePlotLabels
        fpData['avgcoords'] = fpaverageObjectCoords
        fpData['rms'] = fprmsScatter


    recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(recurrences, transient.ra, transient.dec, objectColour = 20)
    avgCoords = {'ra': averageObjectCoords[0]["RA"], 'dec': averageObjectCoords[0]["DEC"], 'ra_sex': ra_to_sex(averageObjectCoords[0]["RA"]), 'dec_sex': dec_to_sex(averageObjectCoords[0]["DEC"]), 'ra_in_hours': ra_in_decimal_hours(averageObjectCoords[0]["RA"])}

    galactic = transform([averageObjectCoords[0]["RA"], averageObjectCoords[0]["DEC"]], J2000toGalactic)
    # Lightcurve data
    lcData = [lcPoints, plotLabels]

    detectionList = transient.detection_list_id

    userListQuerySet = TcsObjectGroups.objects.filter(transient_object_id = transient.id)

    # Grab all the lists of which this object is a member, so that we can exclude these from
    # the user lists to which we want to add this object.
    userListIds = []
    for row in userListQuerySet:
        userListIds.append(row.object_group_id)

    listId = None
    if detectionList:
        listId = detectionList.id

    # Dummy form initialisation
    formSearchObject = SearchForObjectForm()
    form = PromoteAndCommentsForm()

    if request.method == 'POST':
        if 'find_object' in request.POST:
            formSearchObject = SearchForObjectForm(request.POST)
            if formSearchObject.is_valid(): # All validation rules pass
                objectName = formSearchObject.cleaned_data['searchText']
                if len(objectName) > 0 and objectName != '%%':
                    objectsQueryset = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & (Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName)))
                    listHeader = 'Candidates for Followup'
                else:
                    objectsQueryset = AtlasDiffObjects.objects.filter(detection_list_id = listNumber, images_id__isnull = False)
        else:
            form = PromoteAndCommentsForm(request.POST)
            if form.is_valid(): # All validation rules pass
                # Do stuff here
                choice = form.cleaned_data['promote_demote']

                # 2011-02-24 KWS Added Observation Status
                observationStatus = form.cleaned_data['observation_status']
                if observationStatus == 'None':
                    observationStatus = None

                # 2011-04-05 KWS Added User Defined List ID
                userDefinedListId = int(form.cleaned_data['list_add'])

                # 2011-04-13 KWS Grab the URL we posted
                previousURL=form.cleaned_data['redirect_url']

                # 2011-04-14 KWS Grab the lists from which we want to remove this object
                userListsFromWhichToRemoveObject=form.cleaned_data['user_list_membership']

                # 2013-10-29 KWS Added minor checks to make sure that comments not added twice accidentally
                comments = form.cleaned_data['comments']
#                if transient.local_comments and len(transient.local_comments) > 0 and len(comments) > 0 and comments not in transient.local_comments:
#                    comments = transient.local_comments + ': ' + comments
#                elif len(comments) == 0 or (transient.local_comments and comments in transient.local_comments):
#                    comments = transient.local_comments

                #listId = transient.detection_list_id.id
                originalListId = transient.detection_list_id.id

                # Override the listId with the value from the form if it exists

                listId = OBJECT_LISTS[choice]
                if listId < 0:
                    listId = transient.detection_list_id.id

                atlasDesignation = transient.atlas_designation
                surveyField = transient.survey_field
                fieldCounter = transient.followup_counter

                # 2010-12-02 KWS Added check for atlasDesignation.  Don't choose a new designation
                # if we already have one.
                if not atlasDesignation and (listId == GOOD or listId == POSSIBLE or listId == ATTIC or listId == FOLLOWUP):
                    surveyField = 'ATLAS'

                    try:
                       fieldCode = SURVEY_FIELDS[surveyField]
                       # This won't work for ATLAS, so use the field below.
                    except KeyError:
                       # Can't find the field, so record the code as 'XX'
                       fieldCode = 'ATLAS'

                    # Let's assume that there's no field counters table.  Let's try and calculate
                    # what the number should be from the data.

                    followupFlagDate = transient.followup_flag_date
                    if followupFlagDate is None:
                       followupFlagDate = datetime.date.today()
                       objectFlagMonth = datetime.date.today().month
                       objectFlagYear = datetime.date.today().year
                    else:
                       objectFlagMonth = followupFlagDate.month
                       objectFlagYear = followupFlagDate.year

                    # 2019-01-02 KWS bug in comparison of object flag year and object name if object name is previously known object.
#                    fieldCounter = AtlasDiffObjects.objects.filter(followup_flag_date__year = objectFlagYear, survey_field = surveyField, atlas_designation__contains=(objectFlagYear-2000)).aggregate(Max('followup_counter'))['followup_counter__max']
#                    if fieldCounter is None:
#                       # This is the first time we've used the counter
#                       fieldCounter = 1
#                    else:
#                       fieldCounter += 1

                    nameData = getLocalObjectName(settings.NAMESERVER_API_URL, settings.NAMESERVER_TOKEN, transient.id, transient.ra, transient.dec, followupFlagDate.strftime("%Y-%m-%d"), dbName)
                    if nameData:
                        if nameData['status'] == 201 and nameData['counter'] is not None and nameData['name'] is not None:
                            sys.stderr.write("\n%s\n" % nameData['info'])
                            fieldCounter = nameData['counter']
                            atlasDesignation = nameData['name']
                        else:
                            sys.stderr.write("\nStatus = %s. %s\n" % (str(nameData['status']), nameData['info']))
                            request.session['error'] = "ERROR: Nameserver error. Status = %s. %s" % (str(nameData['status']), nameData['info'])
                            redirect_to = "../../error/"
                            return HttpResponseRedirect(redirect_to)  
                    else:
                        sys.stderr.write("\nBad response from the nameserver. Something went wrong.\n")
                        request.session['error'] = "ERROR: Bad response from the Nameserver."
                        redirect_to = "../../error/"
                        return HttpResponseRedirect(redirect_to)  


                    #atlasDesignation = '%d%s%s%s' % (objectFlagYear - 2010, MONTHS[objectFlagMonth - 1], fieldCode, base26(fieldCounter))
                    #atlasDesignation = '%s%d%s' % (fieldCode, objectFlagYear - 2000, base26(fieldCounter))


                # Do an update if the form is valid, regardless of setting of detection list. If the
                # form is valid, it means we've made a choice - if only to add some comments.
                try:
                   AtlasDiffObjects.objects.filter(pk=atlas_diff_objects_id).update(detection_list_id = listId,
                                                                                            survey_field = surveyField,
                                                                                        followup_counter = fieldCounter,
                                                                                       atlas_designation = atlasDesignation,
                                                                                      observation_status = observationStatus, 
                                                                                              updated_by = request.user.username, 
                                                                                           date_modified = datetime.datetime.now()) 

                   if comments:
                       objectComment = TcsObjectComments(transient_object_id_id = transient.id,
                                                                        comment = comments,
                                                                  date_inserted = datetime.datetime.now(),
                                                                       username = request.user.username)

                       objectComment.save()

                except IntegrityError as e:
                   if e[0] == 1062: # Duplicate Key error
                      pass # Do nothing - will eventually raise some errors on the form

                if userDefinedListId > 0:
                    try:
                        userDefinedList = TcsObjectGroupDefinitions.objects.get(pk=userDefinedListId)
                        objGroupId = TcsObjectGroups(transient_object_id=transient, object_group_id=userDefinedList.id)
                        objGroupId.save()

                    except IntegrityError as e:
                        if e[0] == 1062: # Duplicate Key error
                            pass # Do nothing - it's already in the list (can happen if 2 people modify object at same time)


                if userListsFromWhichToRemoveObject:
                    for userListId in userListsFromWhichToRemoveObject:
                        userDefinedList = TcsObjectGroupDefinitions.objects.get(pk=userListId)
                        try:
                            objGroupRow = TcsObjectGroups.objects.get(transient_object_id=transient, object_group_id=userDefinedList.id)
                            if objGroupRow:
                                objGroupRow.delete()

                        except ObjectDoesNotExist as e:
                            # Just in case someone else has already deleted the object before 'Submit' button pressed.
                            pass

                if previousURL and (previousURL.find('/followup/') >= 0 or previousURL.find('/userlist/') >= 0 or previousURL.find('/crossmatch') >= 0 or previousURL.find('/followup_quickview/') >= 0 or previousURL.find('/externalcrossmatches/') > 0 or previousURL.find('/userlist_quickview/') > 0):
                    redirect_to = previousURL
                else:
                    # 2018-02-26 KWS Don't redirect back to list 0 - it takes too long to render
                    if originalListId == 0 or originalListId == 6:
                        redirect_to = '../../followup/4/' # Hard wired to eyeball list
                    else:
                        redirect_to = '../../followup/%d/' % originalListId # redirect back to the original list page

                return HttpResponseRedirect(redirect_to)  
    else:
        # 2011-04-13 KWS Grab the previous URL. E.g. The ordered Followup List.
        #                Send this URL in a hidden field so we can use it on submission.
        previousURL=request.META.get('HTTP_REFERER')

        # 2011-02-24 KWS Default form value added for observation status
        form = PromoteAndCommentsForm(initial={'promote_demote': 'DoNothing',
                                               'observation_status': transient.observation_status,
                                               'list_add': '0',
                                               'redirect_url': previousURL})

        # 2011-04-04 KWS Give the user ONLY those lists of which this object is NOT a member. We already
        #                KNOW which lists this object is a member of.
        listChoices = [(lc.id, lc.description) for lc in TcsObjectGroupDefinitions.objects.exclude(id__in=userListIds)]
        listChoices.append(('0', 'None'))
        form.fields['list_add'].choices = listChoices

        # 2011-04-14 KWS Add the lists of which the object IS a member as a list of checkboxes. It's
        #                probably not wise to keep hitting the database just to render one form, but
        #                speed is not absolutely vital for this operation.
        listMembership = [(lc.id, lc.description) for lc in TcsObjectGroupDefinitions.objects.filter(id__in=userListIds)]
        form.fields['user_list_membership'].choices = listMembership

        # 2011-10-04 KWS Added GARBAGE choices
        if listId == EYEBALL or listId == FASTEYE or listId == SMCLMC or listId == AGN:
            form.fields['promote_demote'].choices = EYEBALL_PROMOTION_CHOICES
        elif listId == FOLLOWUP:
            form.fields['promote_demote'].choices = FOLLOWUP_POST_PROMOTION_CHOICES
        elif listId == GOOD:
            form.fields['promote_demote'].choices = GOOD_POST_PROMOTION_CHOICES
        elif listId == POSSIBLE:
            form.fields['promote_demote'].choices = POSSIBLE_POST_PROMOTION_CHOICES
        elif listId == ATTIC:
            form.fields['promote_demote'].choices = ATTIC_POST_PROMOTION_CHOICES
        elif listId == STAR or listId == HPMSTAR:
            form.fields['promote_demote'].choices = STAR_POST_PROMOTION_CHOICES
        elif listId == GARBAGE:
            form.fields['promote_demote'].choices = GARBAGE_CHOICES
        else:
            form.fields['promote_demote'].choices = FOLLOWUP_POST_PROMOTION_CHOICES


    transient_images = TcsPostageStampImages.objects.filter(image_filename__istartswith = str(transient.id)).exclude(image_filename__istartswith = str(transient.id), image_type__iendswith = 'finder').order_by('-image_filename')

    # 2012-03-24 KWS Grab the existing database connection for cone searches.
    #                We could do this the proper 'Django' way, but we would need
    #                models for all the catalogues.  This is not an option in
    #                the short term.  May consider doing it longer term.
    import sys

    coneSearchRadius = 8.0   # arcsec

    xmObjects = None

    # Grab all objects within 3 arcsec of this one.
    xmList = []
    catalogueName = 'atlas_diff_objects'
    message, xmObjects = coneSearchHTM(transient.ra, transient.dec, coneSearchRadius, catalogueName, queryType = FULL, conn = connection, django = True)

    # The crossmatch Objects xmObjects are a list of two entry lists. The first entry in each row is the separaion.
    # The second entry is the catalogue row dictionary listing the relevant crossmatch.

    if xmObjects:
        numberOfMatches = len(xmObjects)
        # Add the objects into a list of dicts that have consistent names for all catalogues

        for xm in xmObjects:
            sys.stderr.write("\n%s\n" % str(xm))
            # Add to the list all object ids except the current one (which will have
            # a separation of zero).
            if xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]] != transient.id:
                xmList.append({'xmseparation': xm[0], 'xmid': xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]})
                xmid = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]
                xmra = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][1]]
                xmdec = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][2]]
                xmName = xm[1]["atlas_designation"]
                if not xmName:
                    xmName = xmid

                xmDetections = AtlasDiffDetections.objects.filter(atlas_object_id = xmid)
                xmRecurrences = []
                for xmDet in xmDetections:
                    xmRecurrences.append({"RA": xmDet.ra, "DEC": xmDet.dec})

                xmrecurrencePlotData, xmrecurrencePlotLabels, xmaverageObjectCoords, xmrmsScatter = getRecurrenceDataForPlotting(xmRecurrences, transient.ra, transient.dec, secRA = xmra, secDEC = xmdec, secId = xmid, secName = xmName, objectColour = 23)
                recurrencePlotData += xmrecurrencePlotData
                recurrencePlotLabels += xmrecurrencePlotLabels
                averageObjectCoords += xmaverageObjectCoords
                rmsScatter += xmrmsScatter

    recurrenceData = [recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter]

    return render(request, 'atlas/candidate.html',{'transient' : transient, 'table': table, 'images': transient_images, 'form' : form, 'avg_coords': avgCoords, 'lcdata': lcData, 'lcdataforced': lcDataForced, 'lclimits': lcLimits, 'recurrencedata': recurrenceData, 'conesearchold': xmresults['oldDBXmList'], 'olddburl': xmresults['oldDBURL'], 'externalXMs': externalXMs, 'public': public, 'form_searchobject': formSearchObject, 'dbName': dbName, 'finderImages': finderImages, 'processingStatus': processingStatus, 'galactic': galactic, 'fpData': fpData, 'sc': sc, 'gw': gw, 'comments': existingComments})


# 2017-06-16 KWS New DDC format candidate method
@login_required
def candidateddc(request, atlas_diff_objects_id, template_name):
    """candidateddc.

    Args:
        request:
        atlas_diff_objects_id:
        template_name:
    """
    from django.db import connection
    import sys

    # 2021-10-21 KWS Use the Lasair API to do a cone search so we can check for nearby ZTF objects
    from lasair import LasairError, lasair_client as lasair

    transient = get_object_or_404(AtlasDiffObjects, pk=atlas_diff_objects_id)

    token = settings.LASAIR_TOKEN
    # 2022-11-16 KWS Added a new timeout parameter, now available from Lasair client
    #                version v0.0.5+. This should help if Lasair goes offline for any
    #                reason. But extra (Requests)ConnectionError catch needed.
    L = lasair(token, endpoint = 'https://lasair-ztf.lsst.ac.uk/api', timeout = 2.0)

    lasairZTFCrossmatches = None

    # If Lasair connectivity problems arise, comment out the following 4 lines.
    try:
        lasairZTFCrossmatches = L.cone(transient.ra, transient.dec, 2.0, requestType='all')
    except RequestsConnectionError as e:
        # If the API URL is incorrect or times out we will get a connection error.
        sys.stderr.write('Lasair API Connection Error\n')
        sys.stderr.write('%s\n' % str(e))
    except RequestsConnectionTimeoutError as e:
        # If the API times out, we will get a timeout error.
        sys.stderr.write('Lasair API Timeout Error\n')
        sys.stderr.write('%s\n' % str(e))
    except LasairError as e:
        sys.stderr.write('Lasair Error\n')
        sys.stderr.write('%s\n' % str(e))
        
    # 2015-11-17 KWS Get the processing status. If it's not 2, what is it?
    processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
    processingStatus = None
    processingStartTime = None
    if len(processingStatusData) == 1:
        processingStatus = processingStatusData[0].status
        processingStartTime = processingStatusData[0].started

    # 2017-03-21 KWS Get Gravity Wave annotations and Sherlock Classifications
    sc = SherlockClassifications.objects.filter(transient_object_id_id = transient.id)
    # 2017-11-07 KWS Get Sherlock Crossmatches
    sx = SherlockCrossmatches.objects.filter(transient_object_id_id = transient.id)
    gw = TcsGravityEventAnnotations.objects.filter(transient_object_id_id = transient.id).filter(enclosing_contour__lt=100)
    existingComments = TcsObjectComments.objects.filter(transient_object_id = transient.id).order_by('date_inserted')

    # 2013-10-30 KWS Get external crossmatches if they exist
    externalXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id = transient.id).exclude(matched_list = 'Transient Name Server').order_by('external_designation')

    # 2019-10-18 KWS Get TNS crossmatch if it exists. Yes - another unnecessary hit to the database, but quick.
    tnsXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id = transient.id, matched_list = 'Transient Name Server')

    # 2014-03-11 KWS Pick up any Finder images.
    finderImages = TcsPostageStampImages.objects.filter(image_filename__istartswith = str(transient.id), image_type__iendswith = 'finder')

    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')


    # 2013-12-12 KWS Is this a PUBLIC database?
    public = False
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    try:
        detectionLimits = LC_LIMITS[dbName]
    except KeyError as e:
        # Default detections limits for medium deep
        detectionLimits = LC_LIMITS_MD

    #lcPoints, plotLabels, lcLimits = getLCData(transient.id, limits = detectionLimits, lcQuery=LC_POINTS_QUERY_ATLAS_DDC + filterWhereClauseddc(FILTERS))
    lcPoints, lcBlanks, plotLabels, lcLimits = getLCData(transient.id, limits = detectionLimits, conn = connection, ddc = True)

    # 2017-10-02 KWS Since we have started a new database we need to crossmatch the old one.
    #                Have we seen the object before?  And does it have a name??
    coneSearchRadius = 3.6

    xmresults = getNearbyObjectsFromAlternateDatabase(dbName, ALTERNATE_DB_CONNECTIONS, transient, coneSearchRadius)

    # 2016-08-11 KWS Get the Forced Photometry data.  We need to completely rethink how this is queried.
    #                In the past I built custom queries that could be called by scripts or web.  Let's
    #                try just building the query using the ORM.

    forcedPhotometry = AtlasForcedPhotometry.objects.filter(atlas_object_id = transient.id).order_by('mjd_obs')

    # 2016-10-16 KWS Just occasionally the forced photometry will NOT produce
    #                a single point on the lightcurve. In this case we should
    #                skip the forced photometry plot.  (In future, we probably
    #                want to plot the non-detections.
    lcDataForced = []
    lcDataForcedFlux = []
    if forcedPhotometry:
        nonLimitingMagsExist = False
        for row in forcedPhotometry:
            if not row.limiting_mag:
                nonLimitingMagsExist = True
                break
        if nonLimitingMagsExist:
            forcedDetectionData, forcedDetectionDataBlanks, forcedPlotLabels, forcedPlotLimits = organiseAtlasForcedPhotometryForPlotting(forcedPhotometry)
            lcDataForced = [forcedDetectionData, forcedDetectionDataBlanks, forcedPlotLabels, forcedPlotLimits]
            forcedDetectionData, forcedDetectionDataBlanks, forcedPlotLabels, forcedPlotLimits = organiseAtlasForcedFluxPhotometryForPlotting(forcedPhotometry)
            lcDataForcedFlux = [forcedDetectionData, forcedDetectionDataBlanks, forcedPlotLabels, forcedPlotLimits]

    # 2019-06-06 KWS Get the Forced Diff Stack photometry and plot it, if it exists

    forcedDiffStackPhotometry = AtlasStackedForcedPhotometry.objects.filter(atlas_object_id = transient.id).filter(ujy__lt = 10000).filter(ujy__gt = -10000).exclude(ujy = 0, dujy = 999).order_by('mjd')
    lcDataForcedStackFlux = []

    if forcedDiffStackPhotometry:
        forcedStackDetectionData, forcedStackDetectionDataBlanks, forcedStackPlotLabels, forcedStackPlotLimits = organiseAtlasForcedFluxPhotometryForPlottingJT(forcedDiffStackPhotometry)
        lcDataForcedStackFlux = [forcedStackDetectionData, forcedStackDetectionDataBlanks, forcedStackPlotLabels, forcedStackPlotLimits]


    # Get the recurrence data. With the ATLAS schema, we already have all the detections in one place.
    # Note that we should probably aggregate this code together into a function.

    detections = AtlasDetectionsddc.objects.filter(atlas_object_id = transient.id).filter(deprecated__isnull = True)
    table = AtlasDetectionsddcTable(detections)
    #RequestConfig(request, paginate={"per_page": 1}).configure(table)
    RequestConfig(request, paginate=False).configure(table)

    # Convert the detections to a format understandable by the rms calculator.
    recurrences = []
    footprints = []
    for row in detections:
        # 2019-11-02 KWS Exclude all negative detections in average RA/Dec calculation.
        if row.det != 5:
            recurrences.append({"RA": row.ra, "DEC": row.dec})
        footprints.append({"RA": row.atlas_metadata_id.ra, "DEC": row.atlas_metadata_id.dec, "footprintName": row.atlas_metadata_id.obj})

    # 2019-11-02 KWS Redo the recurrences if there are NO positive recurrences.
    if len(recurrences) == 0:
        recurrences = []
        for row in detections:
            recurrences.append({"RA": row.ra, "DEC": row.dec})

    distinctFootprints = set([f['footprintName'] for f in footprints])

    fpData = {}

    if len(distinctFootprints) == 1:
        # We have exactly one footprint
        # Use the average RA and Dec as the input RA and Dec (where the origin will be plotted)
        # (Yes - I know - we are doing this calculation twice!)
        avgRa, avgDec, rms = calculateRMSScatter(footprints)
        fprecurrencePlotData, fprecurrencePlotLabels, fpaverageObjectCoords, fprmsScatter = getRecurrenceDataForPlotting(footprints, avgRa, avgDec, objectColour = 21)
        fpData['plotdata'] = fprecurrencePlotData
        fpData['plotlabels'] = fprecurrencePlotLabels
        fpData['avgcoords'] = fpaverageObjectCoords
        fpData['rms'] = fprmsScatter


    recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(recurrences, transient.ra, transient.dec, objectColour = 20)
    avgCoords = {'ra': averageObjectCoords[0]["RA"], 'dec': averageObjectCoords[0]["DEC"], 'ra_sex': ra_to_sex(averageObjectCoords[0]["RA"]), 'dec_sex': dec_to_sex(averageObjectCoords[0]["DEC"]), 'ra_in_hours': ra_in_decimal_hours(averageObjectCoords[0]["RA"])}

    galactic = transform([averageObjectCoords[0]["RA"], averageObjectCoords[0]["DEC"]], J2000toGalactic)
    # Lightcurve data
    lcData = [lcPoints, lcBlanks, plotLabels]

    detectionList = transient.detection_list_id

    userListQuerySet = TcsObjectGroups.objects.filter(transient_object_id = transient.id)

    # Grab all the lists of which this object is a member, so that we can exclude these from
    # the user lists to which we want to add this object.
    userListIds = []
    for row in userListQuerySet:
        userListIds.append(row.object_group_id)

    listId = None
    if detectionList:
        listId = detectionList.id

    # Dummy form initialisation
    formSearchObject = SearchForObjectForm()
    form = PromoteAndCommentsForm()

    if request.method == 'POST':
        if 'find_object' in request.POST:
            formSearchObject = SearchForObjectForm(request.POST)
            if formSearchObject.is_valid(): # All validation rules pass
                objectName = formSearchObject.cleaned_data['searchText']
                if len(objectName) > 0 and objectName != '%%':
                    objectsQueryset = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & (Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName)))
                    listHeader = 'Candidates for Followup'
                else:
                    objectsQueryset = AtlasDiffObjects.objects.filter(detection_list_id = listNumber, images_id__isnull = False)
        else:
            form = PromoteAndCommentsForm(request.POST)
            if form.is_valid(): # All validation rules pass
                # Do stuff here
                choice = form.cleaned_data['promote_demote']

                # 2011-02-24 KWS Added Observation Status
                observationStatus = form.cleaned_data['observation_status']
                if observationStatus == 'None':
                    observationStatus = None

                # 2011-04-05 KWS Added User Defined List ID
                userDefinedListId = int(form.cleaned_data['list_add'])

                # 2011-04-13 KWS Grab the URL we posted
                previousURL=form.cleaned_data['redirect_url']

                # 2011-04-14 KWS Grab the lists from which we want to remove this object
                userListsFromWhichToRemoveObject=form.cleaned_data['user_list_membership']

                # 2013-10-29 KWS Added minor checks to make sure that comments not added twice accidentally
                comments = form.cleaned_data['comments']
#                if transient.local_comments and len(transient.local_comments) > 0 and len(comments) > 0 and comments not in transient.local_comments:
#                    comments = transient.local_comments + ': ' + comments
#                elif len(comments) == 0 or (transient.local_comments and comments in transient.local_comments):
#                    comments = transient.local_comments

                #listId = transient.detection_list_id.id
                originalListId = transient.detection_list_id.id

                # Override the listId with the value from the form if it exists

                listId = OBJECT_LISTS[choice]
                if listId < 0:
                    listId = transient.detection_list_id.id

                atlasDesignation = transient.atlas_designation
                surveyField = transient.survey_field
                fieldCounter = transient.followup_counter

                # 2010-12-02 KWS Added check for atlasDesignation.  Don't choose a new designation
                # if we already have one.
                if not atlasDesignation and (listId == GOOD or listId == POSSIBLE or listId == ATTIC or listId == FOLLOWUP):
                    surveyField = 'ATLAS'

                    try:
                       fieldCode = SURVEY_FIELDS[surveyField]
                       # This won't work for ATLAS, so use the field below.
                    except KeyError:
                       # Can't find the field, so record the code as 'XX'
                       fieldCode = 'ATLAS'

                    # Let's assume that there's no field counters table.  Let's try and calculate
                    # what the number should be from the data.

                    followupFlagDate = transient.followup_flag_date
                    if followupFlagDate is None:
                       followupFlagDate = datetime.date.today()
                       objectFlagMonth = datetime.date.today().month
                       objectFlagYear = datetime.date.today().year
                    else:
                       objectFlagMonth = followupFlagDate.month
                       objectFlagYear = followupFlagDate.year

                    # Is the object in the old database?? If so, use that name!
                    if xmresults['xmNearestName']:
                        fieldCounter = xmresults['xmNearestCounter']
                        atlasDesignation = xmresults['xmNearestName']
                    else:
#                        fieldCounter = AtlasDiffObjects.objects.filter(followup_flag_date__year = objectFlagYear, survey_field = surveyField, atlas_designation__contains=(objectFlagYear-2000)).aggregate(Max('followup_counter'))['followup_counter__max']
#                        if fieldCounter is None:
#                           # This is the first time we've used the counter
#                           fieldCounter = 1
#                        else:
#                           fieldCounter += 1

                        nameData = getLocalObjectName(settings.NAMESERVER_API_URL, settings.NAMESERVER_TOKEN, transient.id, transient.ra, transient.dec, followupFlagDate.strftime("%Y-%m-%d"), dbName)
                        if nameData:
                            if nameData['status'] == 201 and nameData['counter'] is not None and nameData['name'] is not None:
                                sys.stderr.write("\n%s\n" % nameData['info'])
                                fieldCounter = nameData['counter']
                                atlasDesignation = nameData['name']
                            else:
                                sys.stderr.write("\nStatus = %s. %s\n" % (str(nameData['status']), nameData['info']))
                                request.session['error'] = "ERROR: Nameserver error. Status = %s. %s" % (str(nameData['status']), nameData['info'])
                                redirect_to = "../../error/"
                                return HttpResponseRedirect(redirect_to)
                        else:
                            sys.stderr.write("\nBad response from the nameserver. Something went wrong.\n")
                            request.session['error'] = "ERROR: Bad response from the Nameserver."
                            redirect_to = "../../error/"
                            return HttpResponseRedirect(redirect_to)



                        #atlasDesignation = '%d%s%s%s' % (objectFlagYear - 2010, MONTHS[objectFlagMonth - 1], fieldCode, base26(fieldCounter))
                        #atlasDesignation = '%s%d%s' % (fieldCode, objectFlagYear - 2000, base26(fieldCounter))


                # Do an update if the form is valid, regardless of setting of detection list. If the
                # form is valid, it means we've made a choice - if only to add some comments.
                try:
                   if (originalListId == GOOD) and (listId == FOLLOWUP) and comments.strip() == '':
                       # Did the user add any comments? Ah, ah, ah - blank comments not allowed!
                       request.session['error'] = "WARNING: Please add a comment before promoting to the Followup Targets list, so other users know why it is there!"
                       redirect_to = "../../error/"
                       return HttpResponseRedirect(redirect_to)
                   if originalListId in [EYEBALL, FASTEYE, SMCLMC, STAR, HPMSTAR, AGN, MOVERS] and (listId == POSSIBLE) and comments.strip() == '':
                       # Did the user add any comments? Ah, ah, ah - blank comments not allowed!
                       request.session['error'] = "WARNING: Please add a comment before promoting to the Possible list, so other users know why it is there!"
                       redirect_to = "../../error/"
                       return HttpResponseRedirect(redirect_to)
                   if (originalListId == EYEBALL or originalListId == POSSIBLE or originalListId == ATTIC or originalListId == STAR or originalListId == FASTEYE or originalListId == SMCLMC or originalListId == HPMSTAR) and (listId == GOOD or listId == FOLLOWUP):
                       # Is there an object already in the good or confirmed lists within 2.0 arcsec?
                       message, goodObjects = coneSearchHTM(transient.ra, transient.dec, 2.0, 'atlas_v_followup2', queryType = FULL, conn = connection, django = True)
                       message, confirmedObjects = coneSearchHTM(transient.ra, transient.dec, 2.0, 'atlas_v_followup1', queryType = FULL, conn = connection, django = True)
                       if len(goodObjects) > 0 or len(confirmedObjects) > 0:
                           # Object is already in the good or confirmed lists. Please move to attic.
                           request.session['error'] = "WARNING: Duplicate object is already in the Good List. Please go back and move this to the Attic or Garbage."
                           redirect_to = "../../error/"
                           return HttpResponseRedirect(redirect_to)

                   # 2018-09-28 KWS Ok - we really need to stop updates happening if processing status is not
                   #                set correctly.
                   processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
                   if len(processingStatusData) == 1:
                       processingStatus = processingStatusData[0].status
                       processingStartTime = processingStatusData[0].started
                       if processingStatus == 1:
                           request.session['error'] = "WARNING: Database is busy doing a backup. Please come back later."
                           redirect_to = "../../error/"
                           return HttpResponseRedirect(redirect_to)  
                   AtlasDiffObjects.objects.filter(pk=atlas_diff_objects_id).update(detection_list_id = listId,
                                                                                            survey_field = surveyField,
                                                                                        followup_counter = fieldCounter,
                                                                                       atlas_designation = atlasDesignation,
                                                                                      observation_status = observationStatus, 
                                                                                              updated_by = request.user.username, 
                                                                                           date_modified = datetime.datetime.now()) 

                   if comments:
                       objectComment = TcsObjectComments(transient_object_id_id = transient.id,
                                                                        comment = comments,
                                                                  date_inserted = datetime.datetime.now(),
                                                                       username = request.user.username)

                       objectComment.save()

                   # Register the object on TNS
                   # 2018-05-14 KWS If the previous list was also good (e.g. just adding a comment) don't send a message
                   #                to the TNS daemon.
                   # 2020-02-28 KWS Don't bother registering an object on TNS if the original list was FOLLOWUP and
                   #                we are moving back to GOOD.
                   if listId == GOOD and originalListId != GOOD and originalListId != FOLLOWUP and dbName == 'atlas4':
                       if settings.DAEMONS['tns']['test']:
                           response = sendMessage(settings.DAEMONS['tns']['host'], settings.DAEMONS['tns']['port'], TNS_MESSAGES['SUBMITTEST'])
                       else:
                           response = sendMessage(settings.DAEMONS['tns']['host'], settings.DAEMONS['tns']['port'], TNS_MESSAGES['SUBMIT'])
                       if response:
                           sys.stderr.write('Received %s\n' % repr(response))
                       response = sendMessage(settings.DAEMONS['tns']['host'], settings.DAEMONS['tns']['port'], TNS_MESSAGES['RESULTS'])
                       if response:
                           sys.stderr.write('Received %s\n' % repr(response))


                except IntegrityError as e:
                   if e[0] == 1062: # Duplicate Key error
                      pass # Do nothing - will eventually raise some errors on the form

                if userDefinedListId > 0:
                    try:
                        userDefinedList = TcsObjectGroupDefinitions.objects.get(pk=userDefinedListId)
                        objGroupId = TcsObjectGroups(transient_object_id=transient, object_group_id=userDefinedList.id)
                        objGroupId.save()

                    except IntegrityError as e:
                        if e[0] == 1062: # Duplicate Key error
                            pass # Do nothing - it's already in the list (can happen if 2 people modify object at same time)


                if userListsFromWhichToRemoveObject:
                    for userListId in userListsFromWhichToRemoveObject:
                        userDefinedList = TcsObjectGroupDefinitions.objects.get(pk=userListId)
                        try:
                            objGroupRow = TcsObjectGroups.objects.get(transient_object_id=transient, object_group_id=userDefinedList.id)
                            if objGroupRow:
                                objGroupRow.delete()

                        except ObjectDoesNotExist as e:
                            # Just in case someone else has already deleted the object before 'Submit' button pressed.
                            pass

                if previousURL and (previousURL.find('/followup/') >= 0 or previousURL.find('/userlist/') >= 0 or previousURL.find('/crossmatch') >= 0 or previousURL.find('/followup_quickview/') >= 0 or previousURL.find('/externalcrossmatches/') > 0 or previousURL.find('/userlist_quickview/') > 0 or previousURL.find('/followup_quickview_bs/') >= 0):
                    redirect_to = previousURL
                else:
                    # 2018-02-26 KWS Don't redirect back to list 0 - it takes too long to render
                    if originalListId == 0 or originalListId == 6:
                        redirect_to = '../../followup/4/' # Hard wired to eyeball list
                    else:
                        redirect_to = '../../followup/%d/' % originalListId # redirect back to the original list page

                return HttpResponseRedirect(redirect_to)  
    else:
        # 2011-04-13 KWS Grab the previous URL. E.g. The ordered Followup List.
        #                Send this URL in a hidden field so we can use it on submission.
        previousURL=request.META.get('HTTP_REFERER')

        # 2011-02-24 KWS Default form value added for observation status
        form = PromoteAndCommentsForm(initial={'promote_demote': 'DoNothing',
                                               'observation_status': transient.observation_status,
                                               'list_add': '0',
                                               'redirect_url': previousURL})

        # 2011-04-04 KWS Give the user ONLY those lists of which this object is NOT a member. We already
        #                KNOW which lists this object is a member of.
        listChoices = [(lc.id, lc.description) for lc in TcsObjectGroupDefinitions.objects.exclude(id__in=userListIds)]
        listChoices.append(('0', 'None'))
        form.fields['list_add'].choices = listChoices

        # 2011-04-14 KWS Add the lists of which the object IS a member as a list of checkboxes. It's
        #                probably not wise to keep hitting the database just to render one form, but
        #                speed is not absolutely vital for this operation.
        listMembership = [(lc.id, lc.description) for lc in TcsObjectGroupDefinitions.objects.filter(id__in=userListIds)]
        form.fields['user_list_membership'].choices = listMembership

        # 2011-10-04 KWS Added GARBAGE choices
        if listId == EYEBALL or listId == FASTEYE or listId == SMCLMC or listId == AGN:
            form.fields['promote_demote'].choices = EYEBALL_PROMOTION_CHOICES
        elif listId == FOLLOWUP:
            form.fields['promote_demote'].choices = FOLLOWUP_POST_PROMOTION_CHOICES
        elif listId == GOOD:
            form.fields['promote_demote'].choices = GOOD_POST_PROMOTION_CHOICES
        elif listId == POSSIBLE:
            form.fields['promote_demote'].choices = POSSIBLE_POST_PROMOTION_CHOICES
        elif listId == ATTIC:
            form.fields['promote_demote'].choices = ATTIC_POST_PROMOTION_CHOICES
        elif listId == STAR or listId == HPMSTAR:
            form.fields['promote_demote'].choices = STAR_POST_PROMOTION_CHOICES
        elif listId == GARBAGE:
            form.fields['promote_demote'].choices = GARBAGE_CHOICES
        else:
            form.fields['promote_demote'].choices = FOLLOWUP_POST_PROMOTION_CHOICES


    transient_images = TcsPostageStampImages.objects.filter(image_filename__istartswith = str(transient.id)).exclude(image_filename__istartswith = str(transient.id), image_type__iendswith = 'finder').order_by('-image_filename')

    # 2012-03-24 KWS Grab the existing database connection for cone searches.
    #                We could do this the proper 'Django' way, but we would need
    #                models for all the catalogues.  This is not an option in
    #                the short term.  May consider doing it longer term.
    import sys

    coneSearchRadius = 8.0   # arcsec

    xmObjects = None

    # Grab all objects within 3 arcsec of this one.
    xmList = []
    catalogueName = 'atlas_diff_objects'
    message, xmObjects = coneSearchHTM(transient.ra, transient.dec, coneSearchRadius, catalogueName, queryType = FULL, conn = connection, django = True)

    # The crossmatch Objects xmObjects are a list of two entry lists. The first entry in each row is the separaion.
    # The second entry is the catalogue row dictionary listing the relevant crossmatch.

    if xmObjects:
        numberOfMatches = len(xmObjects)
        # Add the objects into a list of dicts that have consistent names for all catalogues

        for xm in xmObjects:
            sys.stderr.write("\n%s\n" % str(xm))
            # Add to the list all object ids except the current one (which will have
            # a separation of zero).
            if xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]] != transient.id:
                xmList.append({'xmseparation': xm[0], 'xmid': xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]})
                xmid = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]
                xmra = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][1]]
                xmdec = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][2]]
                xmName = xm[1]["atlas_designation"]
                if not xmName:
                    xmName = xmid

                xmDetections = AtlasDetectionsddc.objects.filter(atlas_object_id = xmid)
                xmRecurrences = []
                # 2019-11-02 KWS Only add the crossmatch recurrences if they are positive.
                for xmDet in xmDetections:
                    if xmDet.det != 5:
                        xmRecurrences.append({"RA": xmDet.ra, "DEC": xmDet.dec})

                if len(xmRecurrences) == 0:
                    xmRecurrences = []
                    for xmDet in xmDetections:
                        xmRecurrences.append({"RA": xmDet.ra, "DEC": xmDet.dec})

                xmrecurrencePlotData, xmrecurrencePlotLabels, xmaverageObjectCoords, xmrmsScatter = getRecurrenceDataForPlotting(xmRecurrences, transient.ra, transient.dec, secRA = xmra, secDEC = xmdec, secId = xmid, secName = xmName, objectColour = 23)
                recurrencePlotData += xmrecurrencePlotData
                recurrencePlotLabels += xmrecurrencePlotLabels
                averageObjectCoords += xmaverageObjectCoords
                rmsScatter += xmrmsScatter

    recurrenceData = [recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter]

    return render(request, 'atlas/' + template_name,{'transient' : transient, 'table': table, 'images': transient_images, 'form' : form, 'avg_coords': avgCoords, 'lcdata': lcData, 'lcdataforced': lcDataForced, 'lcdataforcedflux': lcDataForcedFlux, 'lcdataforcedstackflux': lcDataForcedStackFlux, 'lclimits': lcLimits, 'recurrencedata': recurrenceData, 'conesearchold': xmresults['oldDBXmList'], 'olddburl': xmresults['oldDBURL'], 'externalXMs': externalXMs, 'tnsXMs': tnsXMs, 'public': public, 'form_searchobject': formSearchObject, 'dbName': dbName, 'finderImages': finderImages, 'processingStatus': processingStatus, 'galactic': galactic, 'fpData': fpData, 'sc': sc, 'gw': gw, 'comments': existingComments, 'sx': sx, 'lasairZTFCrossmatches': lasairZTFCrossmatches})


def lightcurveplain(request, tcs_transient_objects_id):
    """lightcurveplain.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(AtlasDiffObjects, pk=tcs_transient_objects_id)
    detections = AtlasDiffDetections.objects.filter(atlas_object_id = transient.id)
    table = AtlasDiffDetectionsTable(detections)
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'atlas/lightcurve.txt',{'transient' : transient, 'table' : table }, content_type="text/plain")

def lightcurveplainddc(request, tcs_transient_objects_id):
    """lightcurveplainddc.

    Args:
        request:
        tcs_transient_objects_id:
    """
    import sys
    transient = get_object_or_404(AtlasDiffObjects, pk=tcs_transient_objects_id)
    detections = AtlasDetectionsddc.objects.filter(atlas_object_id = transient.id).order_by('atlas_metadata_id__mjd')
    #t = AtlasDetectionsddcTable(detections)
    #RequestConfig(request, paginate=False).configure(t)
    #for row in t.rows:
    #    #sys.stderr.write('%s\n' % row.det_id)
    #    sys.stderr.write('%s\n' % row.get_cell('det_id'))
    return render(request, 'atlas/lightcurveddc.txt',{ 'table': detections }, content_type="text/plain")

def lightcurveforcedplain(request, tcs_transient_objects_id):
    """lightcurveforcedplain.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(AtlasDiffObjects, pk=tcs_transient_objects_id)
    orderBy = request.GET.get('sort')
    if not orderBy:
        orderBy = 'mjd_obs'
    forcedPhotometry = AtlasForcedPhotometry.objects.filter(atlas_object_id = transient.id).order_by(orderBy)

    # 2020-06-18 KWS Since we don't calculate flux in uJy natively, do it now.
    for row in forcedPhotometry:
#        apfit = row.expname.apfit
#        if apfit is None:
#            apfit = row.apfit
#        exptime = row.expname.texp
#        if exptime is None:
#            exptime = 30.0
#
#        if row.zp is not None and row.major is not None and row.minor is not None and row.peakfit is not None and row.dpeak is not None and apfit is not None and exptime is not None and row.zp is not None:
#            factor = 10**(-0.4*(row.zp+apfit-23.9))
#            uJy = row.peakfit*row.major*row.minor/exptime*factor
#            duJy = row.dpeak*row.major*row.minor/exptime*factor
#            row.uJy = uJy
#            row.duJy = duJy
#        else:
#            row.uJy = None
#            row.duJy = None
#
        # 2020-06-26 KWS STOP quoting mags and dmags if snr below snrlimit - just give snrlimit-sigma limiting mag
        if row.snr is not None and row.snrlimit is not None and row.limiting_mag is not None and row.mag is not None and row.dm is not None and row.dpeak is not None and row.peakfit is not None and row.snr < row.snrlimit and not row.limiting_mag:
            row.limiting_mag = 1
            row.mag = row.mag - 2.5 * log10(row.dpeak * row.snrlimit / row.peakfit)
            row.dm = 0.0
            #row.snr = 3.0


    return render(request, 'atlas/lightcurveforced.txt',{'transient' : transient, 'table' : forcedPhotometry }, content_type="text/plain")

# 2023-06-21 KWS Add a plain text version of the stacked forced photometry.

def lightcurvestackedforcedplain(request, tcs_transient_objects_id):
    """lightcurvestackedforcedplain.
    
    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(AtlasDiffObjects, pk=tcs_transient_objects_id)
    orderBy = request.GET.get('sort')
    if not orderBy:
        orderBy = 'mjd'
    forcedPhotometry = AtlasStackedForcedPhotometry.objects.filter(atlas_object_id = transient.id).order_by(orderBy)

    return render(request, 'atlas/lightcurvestackedforced.txt',{'transient' : transient, 'table' : forcedPhotometry }, content_type="text/plain")


# 2019-02-18 KWS Add ATel template for an object
def atel(request, tcs_transient_objects_id):
    """atel.

    Args:
        request:
        tcs_transient_objects_id:
    """
    import sys
    transient = get_object_or_404(AtlasDiffObjects, pk=tcs_transient_objects_id)

    # By default, grab the information out of the top sherlock_crossmatch. But allow an offset in case sherlock as zoomed in
    # on the wrong host.
    offset = request.GET.get('offset')
    if not offset:
        offset = 0
    else:
        offset = int(offset)

    results = []
    stats = TcsLatestObjectStats.objects.filter(id = transient.id)
    sxms = SherlockCrossmatches.objects.filter(transient_object_id = transient.id).order_by('rank')
    #    results.append({'stats': stats, 'data': row, 'sherlockCrossmatches': sxm, 'sherlockComments': scomments})


    sxm = None
    if len(sxms) > 0 and offset < len(sxms):
        sxm = sxms[offset]

    # 2021-11-19 KWS Grab the PS1 extinction values from the SFD dustmap. NOTE that the dustmap must be
    #                installed. The first time this code runs, it should download the dustmap.
    extinction = {}
    try:
        from gkutils.commonutils import getSFDPanSTARRSATLASExtinction
        extinction = getSFDPanSTARRSATLASExtinction(transient.ra, transient.dec, settings.DUSTMAP_LOCATION, download = True)
        sys.stderr.write("\n%s\n" % str(extinction))

    except ModuleNotFoundError as e:
        pass

    except ImportError as e:
        pass
        
        
    # Use the avarage RA and Dec unless they are not yet set.

    
    # The following variables need to be populated
    # transient['absMag']
    # transient['ra_sex']
    # transient['dec_sex']
    # transient['discoveryMJD']
    # transient['discoveryMag']
    # transient['discoverydMag']
    # transient['other_designation']
    # trasient['discoveryFilter']
    # xm['discoveryDate']
    # xm['discoveryMJD']
    # xm['hostEoffset']
    # xm['hostNOffset']
    # xm['hostOffset']
    # xm['hostOffsetDistance']
    # xm['hostExtinction']
    # xm['hostZ']
    # xm['hostd']
    # xm['hostdmod']

    #scls = SherlockClassifications.objects.filter(transient_object_id = transient.id)

    return render(request, 'atlas/atelfasttrackobject.txt',{'transient': transient, 'sxm': sxm, 'stats': stats, 'extinction': extinction}, content_type="text/plain")


# 2013-02-08 KWS As with lightcurves above, make the colour data available via plain text.

#def colourdataplain(request, tcs_transient_objects_id):
#    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
#    grColour, meangr, grEvolution, riColour, meanri, riEvolution, izColour, meaniz, izEvolution = colourDataPlainQuery(transient.id, applyFudge = True, djangoRawObject = CustomLCPoints)
#    colourData = {}
#    colourData["gr" ] = grColour
#    colourData["grmean" ] = meangr
#    colourData["grtrend"] = grEvolution
#    colourData["ri" ] = riColour
#    colourData["rimean" ] = meanri
#    colourData["ritrend"] = riEvolution
#    colourData["iz" ] = izColour
#    colourData["izmean" ] = meaniz
#    colourData["iztrend"] = izEvolution
#    return render(request, 'psdb/colourdata.txt',{'transient' : transient, 'colourdata' : colourData }, content_type="text/plain")
#
#
## 2015-10-13 KWS Forced photometry plain text query
#def lightcurveforcedplain(request, tcs_transient_objects_id):
#    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
#    mjdLimit = 55347.0 # Hard wired to 31st May 2010
#    # 2012-07-18 KWS Changed this code to call the custom query from a
#    #                dedicated file full of custom queries for lightcurves.
#    recurrences = lightcurveForcedPlainQuery(transient.id, mjdLimit = mjdLimit, djangoRawObject = CustomAllObjectOcurrencesPresentation)
#    return render(request, 'psdb/lightcurveforced.txt',{'transient' : transient, 'table' : recurrences }, content_type="text/plain")
#


@login_required
def obsCatalogue(request, userDefinedListNumber):
    """Create a text only observation catalogue for (e.g.) WHT"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'atlas/obscat.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def obsMediaWiki(request, userDefinedListNumber):
    """Create a text only observation catalogue for (e.g.) WHT"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'atlas/obsmediawiki.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def atelsDiscovery(request, userDefinedListNumber):
    """Create a text only Discovery ATel list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'earliest_mjd'))

    return render(request, 'atlas/atelsdiscovery.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def atelsFast(request, userDefinedListNumber):
    """Create a text only Discovery ATel list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    # Let's do this properly!!  This is horribly inefficient, but we are
    # only dealing with handfulls of objects.
    qs = TcsObjectGroups.objects.filter(object_group_id = userDefinedListNumber)
    results = []
    for row in qs:
        # Get the stats and the sherlock classifications. Use 'filter' not 'get'.
        stats = TcsLatestObjectStats.objects.filter(id = row.transient_object_id)
        sxm = SherlockCrossmatches.objects.filter(transient_object_id = row.transient_object_id, rank = 1)
        scomments = SherlockClassifications.objects.filter(transient_object_id = row.transient_object_id)
        results.append({'stats': stats, 'data': row, 'sherlockCrossmatches': sxm, 'sherlockComments': scomments})


    #table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'earliest_mjd'))

    return render(request, 'atlas/atelsfast.txt',{'table': results, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def visibility(request, userDefinedListNumber):
    """Create a text only Visibility Tool input list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'atlas/visibility.txt',{'table': table, 'rows' : table.rows}, content_type="text/plain")


@login_required
def iobserve(request, userDefinedListNumber):
    """Create a text only Visibility Tool input list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'atlas/iobserve.txt',{'table': table, 'rows' : table.rows}, content_type="text/plain")

@login_required
def heatmap(request, expname, template_name):
    """Generate a heat map for detections within an exposure"""

    import numpy as n
    import json

    xpos = request.GET.get('x')
    try:
        xpos = float(xpos)
    except ValueError as e:
        xpos = None
    except TypeError as e:
        xpos = None

    ypos = request.GET.get('y')
    try:
        ypos = float(ypos)
    except ValueError as e:
        ypos = None
    except TypeError as e:
        ypos = None

    multiplier = request.GET.get('multiplier', '1.6')
    try:
        multiplier = float(multiplier)
    except ValueError as e:
        multiplier = 1.6
    except TypeError as e:
        multiplier = 1.6

    mask = request.GET.get('mask', '0')
    try:
        mask = bool(int(mask))
    except ValueError as e:
        mask = False
    except TypeError as e:
        mask = False

    resolution = 8
    if expname in ['01a','02a','03a','04a']:
        matrix = n.zeros((resolution,resolution), dtype=int)
        data = AtlasHeatmaps.objects.filter(site=expname).order_by('region')
        resolution = int(sqrt(len(data)))
        if resolution not in [8, 16, 32, 64, 128, 256, 512]:
            raise Http404("Resolution of %s pixel map is not an acceptable power of 2" % expname)
    else:
        resolution = 8
        data = AtlasDiffSubcells.objects.filter(obs=expname).order_by('region')

    if len(data) == 0:
        raise Http404("%s exposure not exist" % expname)

    matrix = n.zeros((resolution,resolution), dtype=int)

    for cell in data:
        x = cell.region % resolution
        y = int (cell.region / resolution)
        matrix[y][x] = cell.ndet

    colorBarSpan = 2000

    if expname in ['01a','02a','03a','04a']:
        medValue = n.median(matrix)
        colorBarSpan = multiplier * medValue
        if mask:
            matrix[matrix > colorBarSpan] = 0

    # Now we have a correctly sized list of lists even when some cell data is missing.
    # Also convert into JSON so it can be directly used in javascript.
    heatmap = json.dumps(matrix.tolist())


    return render(request, 'atlas/' + template_name, {'obs': expname, 'heatmap' : heatmap, 'x': xpos, 'y': ypos, 'resolution': resolution, 'colorbarspan': colorBarSpan})

@login_required
# 2018-10-18 KWS Code to generate a JSON table of all the good & confirmed SNe - required by celestial.js
def jsonSNe(request):
    """jsonSNe.

    Args:
        request:
    """
    import json
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    form = SearchForObjectForm()

    querySet = AtlasDiffObjects.objects.filter(atlas_designation__isnull = False, detection_list_id__id__gt = 0, detection_list_id__id__lt = 3)
    features = []                       
    # Can possibly add 'URL': '{% url candidate ' + str(row.id) + ' %}'}, below
    for row in querySet: 
        features.append({'type': 'Feature',
                         'id': row.atlas_designation,
                         'properties': {'name': row.atlas_designation,
                                        'mag': '16',
                                        'desig': '',
                                        'con': '',
                                        'sub': 'M31',
                                        'pop': '',
                                        'type': 'dSph',
                                        'dim': '10',
                                        'str': ''},
                         'geometry': {'type': 'Point',
                                      'coordinates':[row.ra, row.dec]}
                         })

    geojson = json.dumps({'type': 'FeatureCollection', 'features': features})

    return render(request, 'atlas/sne.json',{'geojson': geojson}, content_type="text/plain")


# 2014-01-31 KWS Altered the home page to only show public info for public database.
@login_required
def homepage(request):
    """homepage.

    Args:
        request:
    """
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    form = SearchForObjectForm()

    public = False
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True
        return render(request, 'atlas/index_public.html', {'form_searchobject' : form, 'public': public})
    else:
        return render(request, 'atlas/index_bs_celestial.html', {'form_searchobject' : form, 'public': public})

# 2018-09-28 KWS New error page.
@login_required
def errorpage(request):
    """errorpage.

    Args:
        request:
    """

    # Add a default message of "ERROR" but read the session variable for a real error, then delete it.
    message = "ERROR"
    if 'error' in request.session:
        message = request.session.get('error')
        del request.session['error']

    return render(request, 'atlas/error.html', {'error_message': message})

@login_required
def temporaryHomepage(request):
    """temporaryHomepage.

    Args:
        request:
    """
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    public = False
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True
        return render(request, 'atlas/index_public_for_approval.html', {'public': public})
    else:
        return render(request, 'atlas/index_bs.html', {'public': public})


@login_required
def redirectedHomepage(request):
    """redirectedHomepage.

    Args:
        request:
    """
    redirect_to = './psdb/' 
    return HttpResponseRedirect(redirect_to)
    
@login_required
def reportspage(request):
    """reportspage.

    Args:
        request:
    """
    return render(request, 'atlas/reports.html')
    


# DSS2 request image function
def dss2(request, tcs_transient_objects_id):
    """dss2.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(AtlasDiffObjects, pk=tcs_transient_objects_id)
    (ra_sex, dec_sex) = coords_dec_to_sex(transient.ra_psf, transient.dec_psf, ' ')
    x = '10'
    y = '10'
    page = getDSS2Image(ra_sex, dec_sex, x, y)
    return render(request, 'atlas/dss2.html', {'page': page})


class FollowupRawTable(tables2.Table):
    """FollowupRawTable.
    """

    id = tables2.LinkColumn('candidate', args=[A('id')])
    #ID = tables2.Column(visible=False)
    ra = tables2.Column()
    dec = tables2.Column()
#    ra_sex = tables2.Column('ra_sex', order_by='ra')
#    dec_sex = tables2.Column('dec_sex', order_by='dec')
    observation_status = tables2.Column(verbose_name="Spectral Type")
    object_classification = tables2.Column(visible=False, verbose_name="Machine Classification")
    catalogue = tables2.Column(visible=False)
    catalogue_object_id = tables2.Column(visible=False, verbose_name="Nearest Object")
    followup_flag_date = tables2.Column(verbose_name="Flag Date")
    separation = tables2.Column(visible=False, verbose_name="Separation (arcsec)")
    realbogus_factor = tables2.Column(verbose_name="RB Factor")
    rb_pix = tables2.Column(verbose_name="RB Factor 2")
#    external_crossmatches = tables2.Column(verbose_name="External Crossmatches", sortable=False)
    external_crossmatches = tables2.Column(verbose_name="External Crossmatches")
    discovery_target = tables2.Column(visible=False)

    # Added these methods in place of using @property
    def render_ra(self, value):
        """render_ra.

        Args:
            value:
        """
        ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec(self, value):
        """render_dec.

        Args:
            value:
        """
        dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    def render_object_classification(self, value):
        """render_object_classification.

        Args:
            value:
        """
        object_definition = getFlagDefs(value, FLAGS, delimiter = ' ')
        return object_definition

#    # 2016-01-21 KWS Add an external crossmatches check
#    def render_external_crossmatches(self, value):
#        """This is a Hack to get all the external crossmatches per row. Note that
#           it only gets executed 100 times (for each page) so it is not disastrous
#           for database performance.
#        """
#        xms = TcsCrossMatchesExternal.objects.filter(transient_object_id__id=self.id).order_by('external_designation')
#        names = xms.values_list("external_designation", flat=True)
#        nameColumn = ", ".join(names)
#        sys.stderr.write('\nOBJECT (%s) = %s\n' % (self.id, nameColumn))
#        return nameColumn

    class Meta:
        """Meta.
        """

        model = FollowupRaw
        attrs = {'class': 'followuplists_standardview'}



def followupList3(request, listNumber):
    """followupList3.

    Args:
        request:
        listNumber:
    """

    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description

    public = False
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    objectName = None

    if request.method == 'POST':
        form = SearchForObjectForm(request.POST)
        if form.is_valid(): # All validation rules pass
            # Do stuff here

            objectName = form.cleaned_data['searchText']
            if len(objectName) > 0 and objectName != '%%':
                # 2013-07-23 KWS Altered query to extract the relevant IDs from the tcs_transient_objects table
                #                in the hope that this will speed up the query.
                #transients_queryset = TcsTransientObjects.objects.filter(Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName))
                #initial_queryset = WebViewFollowupTransients.objects.filter(pk__in=transients_queryset.values_list('id'))
                listHeader = 'Candidates for Followup'
            else:
                initial_queryset = followupListQuery(listNumber, djangoRawObject = FollowupRaw)

    else:
        if objectName:
            form = SearchForObjectForm(initial={'searchText': objectName})
        else:
            form = SearchForObjectForm()

        initial_queryset = followupListQuery(listNumber, djangoRawObject = FollowupRaw)

    table = FollowupRawTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    RequestConfig(request, paginate={"per_page": 100}).configure(table)
    return render(request, 'atlas/followup.html', {'table': table, 'rows' : table.rows, 'listHeader' : listHeader, 'form' : form, 'public': public})

# def followupList2(request, listNumber):
#     """followupList2.
# 
#     Args:
#         request:
#         listNumber:
#     """
# 
#     detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
#     listHeader = detectionListRow.description
# 
#     public = False
#     dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
#     if 'atlaspublic' in dbName or 'kws' in dbName:
#         public = True
# 
#     objectName = None
#     page = request.GET.get('page')
#     if page is None:
#         page = 1
#     else:
#         page = int(page)
# 
# 
#     if request.method == 'POST':
#         form = SearchForObjectForm(request.POST)
#         if form.is_valid(): # All validation rules pass
#             # Do stuff here
# 
#             objectName = form.cleaned_data['searchText']
#             if len(objectName) > 0 and objectName != '%%':
#                 listHeader = 'Candidates for Followup'
#             else:
#                 sql = FOLLOWUP_LIST_QUERY % listNumber
#                 
# 
#     else:
#         if objectName:
#             form = SearchForObjectForm(initial={'searchText': objectName})
#         else:
#             form = SearchForObjectForm()
# 
#         sql = FOLLOWUP_LIST_QUERY % listNumber
# 
#     order_by = request.GET.get('sort')
#     paginator = SqlPaginator(sql, FollowupRaw, page=page, order_by=order_by, per_page=100)
#     count = paginator.count
# 
#     try:
#         table = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         table = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         table = paginator.page(paginator.num_pages)
# 
#     return render(request, 'atlas/followup2.html', {'table': table, 'count': count, 'listHeader' : listHeader, 'form' : form, 'public': public})
# 
# 

def followup_bypass_django_tables(request, listNumber):
    """followup_bypass_django_tables.

    Args:
        request:
        listNumber:
    """
    import sys
    from django.db import connection
    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description
    #data = TcsLatestObjectStats.objects.filter(id__detection_list_id = listNumber).order_by('id__followup_id').select_related()
    data = followupClassList[int(listNumber)].objects.all().order_by('-rank')
    #data = AtlasDiffObjects.objects.filter(detection_list_id = listNumber).order_by('followup_id')
    paginator = Paginator(data, 100)
    page = request.GET.get('page')
    try:
        subdata = paginator.page(page)

    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subdata = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        subdata = paginator.page(paginator.num_pages)

    return render(request, 'atlas/followup_bypass_django_tables.html', {'subdata': subdata, 'connection': connection})


class WebViewFollowupTransientsTable(tables2.Table):
    """WebViewFollowupTransientsTable.
    """

    idtxt = tables2.Column(accessor='id', visible=False)
    id = tables2.LinkColumn('candidate', args=[A('id')])
    ra = tables2.Column()
    dec = tables2.Column()
    ra_avg = tables2.Column(visible=False)
    dec_avg = tables2.Column(visible=False)
    atlas_designation = tables2.Column(default='')
    other_designation = tables2.Column(default='')
    observation_status = tables2.Column(verbose_name="Spectral Type")
    object_classification = tables2.Column(visible=False, verbose_name="Machine Classification")
    sherlockClassification = tables2.Column(verbose_name="Context Classification")
    catalogue = tables2.Column(visible=False)
    catalogue_object_id = tables2.Column(visible=False, verbose_name="Nearest Object")
    followup_flag_date = tables2.Column(verbose_name="Flag Date")
    separation = tables2.Column(visible=False, verbose_name="Separation (arcsec)")
    realbogus_factor = tables2.Column(verbose_name="RB Factor")
    rb_pix = tables2.Column(verbose_name="RB Factor 2")
    date_modified = tables2.Column(visible=False)
    external_crossmatches = tables2.Column(verbose_name="External Crossmatches")
    discovery_target = tables2.Column(visible=False)
    rms = tables2.Column()
    images_id = tables2.Column(visible=False)
    detection_list_id = tables2.Column(visible=False)

    # Added these methods in place of using @property
    def render_ra(self, value, record):
        """render_ra.

        Args:
            value:
            record:
        """
        if record.ra_avg:
            ra_in_sex = ra_to_sex (record.ra_avg)
        else:
            ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec(self, value, record):
        """render_dec.

        Args:
            value:
            record:
        """
        if record.dec_avg:
            dec_in_sex = dec_to_sex (record.dec_avg)
        else:
            dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    def render_object_classification(self, value):
        """render_object_classification.

        Args:
            value:
        """
        object_definition = getFlagDefs(value, FLAGS, delimiter = ' ')
        return object_definition

    def render_realbogus_factor(self, value):
        """render_realbogus_factor.

        Args:
            value:
        """
        return '%.3f' % value

    def render_rb_pix(self, value):
        """render_rb_pix.

        Args:
            value:
        """
        return '%.3f' % value

    def render_separation(self, value):
        """render_separation.

        Args:
            value:
        """
        return '%.2f' % value

    def render_earliest_mjd(self, value):
        """render_earliest_mjd.

        Args:
            value:
        """
        return '%.5f' % value

    def render_latest_mjd(self, value):
        """render_latest_mjd.

        Args:
            value:
        """
        return '%.5f' % value

    def render_other_designation(self, value, record):
        """render_other_designation.

        Args:
            value:
            record:
        """
        prefix = 'AT'
        if record.observation_status and ('SN' in record.observation_status or 'I' in record.observation_status):
            prefix = 'SN'
        return prefix + value

    class Meta:
        """Meta.
        """

        model = WebViewAbstractFollowup
        #attrs = {'class': 'followuplists_standardview'}
        template_name = "bootstrap4_django_tables2_atlas.html"

# This class is a generic template for all the prioritised followup transients.

followupClassList = [WebViewFollowupTransients0,
                     WebViewFollowupTransients1,
                     WebViewFollowupTransients2,
                     WebViewFollowupTransients3,
                     WebViewFollowupTransients4,
                     WebViewFollowupTransients5,
                     WebViewFollowupTransients6,
                     WebViewFollowupTransients7,
                     WebViewFollowupTransients8,
                     WebViewFollowupTransients9,
                     WebViewFollowupTransients10,
                     WebViewFollowupTransients11]


@login_required
def followupList(request, listNumber):
    """followupList.

    Args:
        request:
        listNumber:
    """

    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description

    public = False
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    objectName = None

    # 2019-07-31 KWS Add ability to filter on a GW event.
    queryFilterGW = filterGetGWParameters(request, {})

    if request.method == 'POST':
        form = SearchForObjectForm(request.POST)
        if form.is_valid(): # All validation rules pass
            # Do stuff here

            objectName = form.cleaned_data['searchText']
            if len(objectName) > 0 and objectName != '%%':
                # 2013-07-23 KWS Altered query to extract the relevant IDs from the tcs_transient_objects table
                #                in the hope that this will speed up the query.
                #transients_queryset = TcsTransientObjects.objects.filter(Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName))
                #initial_queryset = WebViewFollowupTransients.objects.filter(pk__in=transients_queryset.values_list('id'))
                listHeader = 'Candidates for Followup'
            else:
                if queryFilterGW:
                    gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=listNumber).filter(**queryFilterGW)
                    gwTaggedObjects = [x.transient_object_id_id for x in gw]
                    if len(gwTaggedObjects) == 0:
                        # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
                        gwTaggedObjects = [1]
                    initial_queryset = followupClassList[int(listNumber)].objects.filter(id__in=gwTaggedObjects)
                else:
                    queryFilter = filterGetParameters(request, {})
                    initial_queryset = followupClassList[int(listNumber)].objects.all().filter(**queryFilter)
                    #initial_queryset = followupClassList[int(listNumber)].objects.all()

    else:
        if objectName:
            form = SearchForObjectForm(initial={'searchText': objectName})
        else:
            form = SearchForObjectForm()

        if queryFilterGW:
            gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=listNumber).filter(**queryFilterGW)
            gwTaggedObjects = [x.transient_object_id_id for x in gw]
            if len(gwTaggedObjects) == 0:
                # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
                gwTaggedObjects = [1]
            initial_queryset = followupClassList[int(listNumber)].objects.filter(id__in=gwTaggedObjects)
        else:
            queryFilter = filterGetParameters(request, {})
            initial_queryset = followupClassList[int(listNumber)].objects.all().filter(**queryFilter)
            #initial_queryset = followupClassList[int(listNumber)].objects.all()

    table = WebViewFollowupTransientsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)
    return render(request, 'atlas/followup_bs.html', {'table': table, 'rows' : table.rows, 'listHeader' : listHeader, 'form_searchobject' : form, 'public': public})


# No login required at the moment!
def followuptxt(request, listNumber):
    """Create a text only catalogue of the followup transients"""

    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description
    initial_queryset = followupClassList[int(listNumber)].objects.all()
    table = WebViewFollowupTransientsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    RequestConfig(request, paginate=False).configure(table)

    return render(request, 'atlas/followup.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")

def followupsubsettxt(request, listNumber):
    """Create a text only catalogue of the followup transients"""

    order_by = request.GET.get('sort', '-rank')
    resultSet = followupClassList[int(listNumber)].objects.all().order_by(order_by)

    return render(request, 'atlas/followup_subset.txt',{'rows' : resultSet}, content_type="text/plain")

# 2016-07-26 KWS Introduced the PROPER way to join TcsLatestObjectStats
#                and AtlasDiffObjects. There is no real requirement for
#                an outer join.  This will eventually replace the
#                WebViewFollowupTransientsTable and should speed up the
#                actual database queries!
class TcsLatestObjectStatsTable(tables2.Table):
    """TcsLatestObjectStatsTable.
    """


    id = tables2.Column()
    ra = tables2.Column(accessor="ra_avg")
    dec = tables2.Column(accessor="dec_avg")
    ra_deg = tables2.Column(accessor="ra_avg")
    dec_deg = tables2.Column(accessor="dec_avg")
    earliest_mjd = tables2.Column()
    earliest_mag = tables2.Column()
    earliest_filter = tables2.Column()
    latest_mjd = tables2.Column()
    latest_mag = tables2.Column()
    latest_filter = tables2.Column()
    catalogue = tables2.Column(visible=False)
    catalogue_object_id = tables2.Column(visible=False)
    separation = tables2.Column(visible=False)
    discovery_target = tables2.Column()
    rms = tables2.Column()
    external_crossmatches = tables2.Column(verbose_name="External Crossmatches")
    # Foreign keys
    rank = tables2.Column(accessor="id.followup_id")
    atlas_designation = tables2.Column(accessor="id.atlas_designation", default='')
    other_designation = tables2.Column(accessor="id.other_designation", default='')
    other_designation_prefix = tables2.Column(accessor="id.other_designation", default='')
    observation_status = tables2.Column(accessor="id.observation_status", verbose_name="Spectral Type", default='')
    object_classification = tables2.Column(visible=False, accessor="id.object_classification", verbose_name="Machine Classification")
    followup_flag_date = tables2.Column(accessor="id.followup_flag_date", verbose_name="Flag Date")
    realbogus_factor = tables2.Column(accessor="id.realbogus_factor", verbose_name="RB Factor")
    rb_pix = tables2.Column(accessor="id.rb_pix", verbose_name="RB Factor 2")
    date_modified = tables2.Column(accessor="id.date_modified", verbose_name="Date Modified")
    target = tables2.Column(accessor="id.images_id.target", default='')
    ref = tables2.Column(accessor="id.images_id.ref", default='')
    diff = tables2.Column(accessor="id.images_id.diff", default='')
    earliest_mjd_date = tables2.Column(accessor='earliest_mjd', visible=False)
    latest_mjd_date = tables2.Column(accessor='latest_mjd', visible=False)

    # Added these methods in place of using @property
    def render_ra(self, value, record):
        """render_ra.

        Args:
            value:
            record:
        """
        ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec(self, value, record):
        """render_dec.

        Args:
            value:
            record:
        """
        dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    def render_object_classification(self, value):
        """render_object_classification.

        Args:
            value:
        """
        object_definition = getFlagDefs(value, FLAGS, delimiter = ' ')
        return object_definition

    def render_realbogus_factor(self, value):
        """render_realbogus_factor.

        Args:
            value:
        """
        return '%.3f' % value

    def render_rb_pix(self, value):
        """render_rb_pix.

        Args:
            value:
        """
        return '%.3f' % value

    def render_separation(self, value):
        """render_separation.

        Args:
            value:
        """
        return '%.2f' % value

    def render_earliest_mjd(self, value):
        """render_earliest_mjd.

        Args:
            value:
        """
        return '%.5f' % value

    def render_earliest_mjd_date(self, value):
        """render_earliest_mjd_date.

        Args:
            value:
        """
        dateFraction = getDateFractionMJD(value, delimiter = '-')
        return dateFraction

    def render_latest_mjd(self, value):
        """render_latest_mjd.

        Args:
            value:
        """
        return '%.5f' % value

    def render_latest_mjd_date(self, value):
        """render_latest_mjd_date.

        Args:
            value:
        """
        dateFraction = getDateFractionMJD(value, delimiter = '-')
        return dateFraction

    def render_other_designation_prefix(self, value, record):
        """render_other_designation_prefix.

        Args:
            value:
            record:
        """
        prefix = 'AT'
        if record.id.observation_status and ('SN' in record.id.observation_status):
            prefix = 'SN'
        return prefix + value

    class Meta:
        """Meta.
        """

        model = TcsLatestObjectStats
        attrs = {'class': 'followuplists_standardview'}

# 2016-07-27 KWS Need a table to connect detections with metadata (MJD)
#                Note that tables include all existing model columns by
#                default. Changes to definitions or FK columns should be
#                defined below.
#                Note that I tested this against a Django tables v1 table
#                for speed. This is 2 x faster than old Django tables.
#                It's still VERY slow though. Takes ~ 25 seconds to
#                render 8500 rows.
class AtlasDiffDetectionsTable2(tables2.Table):
    """AtlasDiffDetectionsTable2.
    """


    id = tables2.Column()
    ra_deg = tables2.Column(accessor="ra")
    dec_deg = tables2.Column(accessor="dec")
    # Foreign key refs from AtlasDiffObjects
    detection_list_id = tables2.Column(accessor="atlas_object_id.detection_list_id")
    rank = tables2.Column(accessor="atlas_object_id.followup_id")
    atlas_designation = tables2.Column(accessor="atlas_object_id.atlas_designation", default='')
    other_designation = tables2.Column(accessor="atlas_object_id.other_designation", default='')
    # Foreign key refs from AtlasMetadata
    filename = tables2.Column(accessor="atlas_metadata_id.filename", default='')
    expname = tables2.Column(accessor="atlas_metadata_id.expname", default='')
    object = tables2.Column(accessor="atlas_metadata_id.object", default='')
    mjd_obs = tables2.Column(accessor="atlas_metadata_id.mjd_obs")
    filter = tables2.Column(accessor="atlas_metadata_id.filter")
    exptime = tables2.Column(accessor="atlas_metadata_id.exptime")
    zp = tables2.Column(accessor="atlas_metadata_id.zp")
    mag5sig = tables2.Column(accessor="atlas_metadata_id.mag5sig")

    def render_ra(self, value, record):
        """render_ra.

        Args:
            value:
            record:
        """
        ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec(self, value, record):
        """render_dec.

        Args:
            value:
            record:
        """
        dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    class Meta:
        """Meta.
        """

        model = AtlasDiffDetections
        # HTML addributes to add to <TABLE> tag. For use by CSS.
        attrs = {'class': 'followuplists_standardview'}


def pesstosummary(request):
    """Create the PESSTO summary table - exclusively from lists 2 and 1"""

    queryFilter = {}
    queryFilter = filterGetParameters(request, queryFilter, prefix = 'id__')
    qQueryFilter = (Q(id__detection_list_id = 1) | Q(id__detection_list_id = 2)) & Q(**queryFilter)
    initial_queryset = TcsLatestObjectStats.objects.filter(qQueryFilter).exclude(id__atlas_designation__isnull = True).order_by('-id__followup_id')
    #table = TcsLatestObjectStatsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    #RequestConfig(request, paginate=False).configure(table)
    #initial_queryset = AtlasVSummaryPessto.objects.all().order_by('-rank')

    # 2018-08-17 KWS Bypass Django tables and use the query directly.
    # 2020-10-20 KWS We don't NEED all the data.  We could paginate and also have
    #                a query filter in the same way we already do for followup_quickview.

    return render(request, 'atlas/pesstosummary.txt',{'table': initial_queryset}, content_type="text/plain")

def summarycsv(request, listNumber):
    """Create the PESSTO summary table - exclusively from lists 2 and 1"""

    initial_queryset = TcsLatestObjectStats.objects.filter(id__detection_list_id = listNumber)
    table = TcsLatestObjectStatsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    RequestConfig(request, paginate=False).configure(table)

    return render(request, 'atlas/summary.csv',{'table': table, 'rows' : table.rows}, content_type="text/plain")

def pesstorecurrences(request):
    """Create the PESSTO recurrences table"""
    # Bypass Django tables and render directly. It's at least double the speed.
    initial_queryset = AtlasDiffDetections.objects.filter(Q(atlas_object_id__detection_list_id = 1) | Q(atlas_object_id__detection_list_id = 2)).exclude(atlas_object_id__atlas_designation__isnull = True).select_related('atlas_object_id','atlas_metadata_id').order_by('-atlas_object_id__followup_id')
    #initial_queryset = AtlasDiffDetections.objects.filter(Q(atlas_object_id__detection_list_id = 1) | Q(atlas_object_id__detection_list_id = 0)).select_related('atlas_object_id','atlas_metadata_id').order_by('-atlas_object_id__followup_id')

    return render(request, 'atlas/pesstorecurrences.txt',{'table': initial_queryset}, content_type="text/plain")

def pesstorecurrencesddc(request):
    """Create the PESSTO recurrences table"""
    #initial_queryset = AtlasDetectionsddc.objects.filter(Q(atlas_object_id__detection_list_id = 1) | Q(atlas_object_id__detection_list_id = 2)).exclude(atlas_object_id__atlas_designation__isnull = True).select_related('atlas_object_id','atlas_metadata_id').order_by('-atlas_object_id__followup_id')
    # 2018-08-01 KWS Use custom view, not nasty ORM code!
    initial_queryset = AtlasVRecurrencesddcPessto.objects.all().order_by('-rank', '-mjd')

    return render(request, 'atlas/pesstorecurrencesddc.txt',{'table': initial_queryset}, content_type="text/plain")

@login_required
def atelsDiscovery(request, userDefinedListNumber):
    """Create a text only Discovery ATel list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))
    RequestConfig(request, paginate=False).configure(table)

    return render(request, 'atlas/atelsdiscovery.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")

class TcsCrossMatchesExternalTable(tables2.Table):
    """TcsCrossMatchesExternalTable.
    """

    idtxt = tables2.Column(accessor="id", visible=False)
    id = tables2.LinkColumn('candidate', args=[A('id')])
    transient_object_id = tables2.Column(accessor="transient_object_id", verbose_name="Internal ID")
    external_designation = tables2.Column(verbose_name="External Designation")
    type = tables2.Column(accessor='type')
    host_galaxy = tables2.Column(accessor="host_galaxy")
    mag = tables2.Column(accessor='mag')
    discoverer = tables2.Column(accessor='discoverer')
    matched_list = tables2.Column(accessor='matched_list')
    other_info = tables2.Column(accessor='other_info')
    separation = tables2.Column(verbose_name="Separation")
    comments = tables2.Column(accessor="comments")
    url = tables2.Column(accessor="url", visible=False)
    #transient_object_id__local_designation = tables2.Column(accessor="local_designation", verbose_name="QUB Name")
    transient_object_id__atlas_designation = tables2.Column(accessor="atlas_designation", verbose_name="ATLAS Name")
    transient_object_id__detection_list_id = tables2.Column(accessor="detection_list_id", verbose_name="QUB List")
    transient_object_id__ra = tables2.Column(accessor='ra', verbose_name="QUB RA")
    transient_object_id__dec = tables2.Column(accessor='dec', verbose_name="QUB DEC")

    def render_ra(self, value, record):
        """render_ra.

        Args:
            value:
            record:
        """
        if record.ra_avg:
            ra_in_sex = ra_to_sex (record.ra_avg)
        else:
            ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec(self, value, record):
        """render_dec.

        Args:
            value:
            record:
        """
        if record.dec_avg:
            dec_in_sex = dec_to_sex (record.dec_avg)
        else:
            dec_in_sex = dec_to_sex (value)
        return dec_in_sex


    class Meta:
        """Meta.
        """

        model = TcsCrossMatchesExternal

@login_required
def displayExternalCrossmatches(request):
    """displayExternalCrossmatches.

    Args:
        request:
    """
    crossmatches = TcsCrossMatchesExternal.objects.all().order_by('transient_object_id')
    table = TcsCrossMatchesExternalTable(crossmatches, order_by=request.GET.get('sort', '-atlas_designation'))
    crossmatchTitle = 'External Transient Crossmatches'
    return render(request, 'atlas/crossmatch_external.html', {'table': table, 'rows' : table.rows, 'crossmatchTitle': crossmatchTitle})


# 2016-06-15 KWS Added all the followup quickview code. For the time being use
#                django-tables.  We'll upgrade to django-tables2 when we have
#                the code running properly.

class AtlasDiffObjectsTable(tables2.Table):
    """AtlasDiffObjectsTable.
    """

    IMAGE_TEMPLATE = """<img id="stampimages" src="{{ MEDIA_URL }}images/data/{{ dbname }}/{{ record.images_id.whole_mjd }}/{{ record.images_id.%s }}.jpeg" alt="triplet" title="{{ record.images_id.pss_filename }}" onerror="this.src='{{ STATIC_URL }}images/image_not_available.jpeg';" height="200" />""" % 'diff'

    id = tables2.Column(accessor='id', visible = False)
    followup_id = tables2.LinkColumn('candidate', accessor='followup_id', verbose_name="Followup ID", args=[A('id')])
    followup_flag_date = tables2.Column(accessor='followup_flag_date', verbose_name='Flag Date')
    ra = tables2.Column(accessor='ra', verbose_name='ra')
    dec = tables2.Column(accessor='dec', verbose_name='dec')
    object_classification = tables2.Column(visible=False, accessor='object_classification', verbose_name='Type')
    sherlockClassification = tables2.Column(verbose_name='Context Classification')
    observation_status = tables2.Column(verbose_name="Spec Type")
    atlas_designation = tables2.Column(accessor='atlas_designation', verbose_name='ATLAS Name')
    other_designation = tables2.Column(accessor='other_designation', verbose_name='TNS Name')
    current_trend = tables2.Column(accessor='current_trend', verbose_name='Trend')
    images_id = tables2.Column(visible=False)

    target = tables2.TemplateColumn(getDjangoTables2ImageTemplate('target'), orderable = False)
    ref = tables2.TemplateColumn(getDjangoTables2ImageTemplate('ref'), orderable = False)
    diff = tables2.TemplateColumn(getDjangoTables2ImageTemplate('diff'), orderable = False)

    date_modified = tables2.Column(accessor="date_modified", visible=False)
    mjd_obs = tables2.Column(accessor='images_id__mjd_obs', verbose_name='Recent Triplet MJD', visible = False)
    realbogus_factor = tables2.Column(accessor='realbogus_factor', verbose_name='RB (DEW)')
    rb_pix = tables2.Column(accessor="rb_pix", verbose_name='RB (TF)')
    detection_list_id = tables2.Column(accessor="detection_list_id", visible=False)

    # Added these methods in place of using @property
    def render_ra(self, value, record):
        """render_ra.

        Args:
            value:
            record:
        """
        ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec(self, value, record):
        """render_dec.

        Args:
            value:
            record:
        """
        dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    def render_realbogus_factor(self, value):
        """render_realbogus_factor.

        Args:
            value:
        """
        return '%.3f' % value

    def render_rb_pix(self, value):
        """render_rb_pix.

        Args:
            value:
        """
        return '%.3f' % value

    def render_other_designation(self, value, record):
        """render_other_designation.

        Args:
            value:
            record:
        """
        prefix = 'AT'
        if record.observation_status and ('SN' in record.observation_status or 'I' in record.observation_status):
            prefix = 'SN'
        return prefix + value


    class Meta:
        """Meta.
        """

        model = AtlasDiffObjects
        exclude = ['detection_id', 'htm16id', 'jtindex', 'date_inserted', 'date_modified', 'processing_flags', 'updated_by', 'followup_priority', 'external_reference_id',  'survey_field', 'followup_counter', 'ndetections', 'local_comments'] 
        template_name = "bootstrap4_django_tables2_atlas.html"


class AtlasDiffObjectsTableAtticOptions(AtlasDiffObjectsTable):
    """AtlasDiffObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    P = tables2.TemplateColumn(getChoiceSelectorTemplate("P")['template'], verbose_name="P", orderable=False, attrs=getChoiceSelectorTemplate("P")['attrs'])
    T = tables2.TemplateColumn(getChoiceSelectorTemplate("T")['template'], verbose_name="T", orderable=False, attrs=getChoiceSelectorTemplate("T")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class AtlasDiffObjectsTableEyeballOptions(AtlasDiffObjectsTable):
    """AtlasDiffObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    S = tables2.TemplateColumn(getChoiceSelectorTemplate("S")['template'], verbose_name="S", orderable=False, attrs=getChoiceSelectorTemplate("S")['attrs'])
    P = tables2.TemplateColumn(getChoiceSelectorTemplate("P")['template'], verbose_name="P", orderable=False, attrs=getChoiceSelectorTemplate("P")['attrs'])
    A = tables2.TemplateColumn(getChoiceSelectorTemplate("A")['template'], verbose_name="A", orderable=False, attrs=getChoiceSelectorTemplate("A")['attrs'])
    T = tables2.TemplateColumn(getChoiceSelectorTemplate("T")['template'], verbose_name="T", orderable=False, attrs=getChoiceSelectorTemplate("T")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class AtlasDiffObjectsTablePossibleOptions(AtlasDiffObjectsTable):
    """AtlasDiffObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    S = tables2.TemplateColumn(getChoiceSelectorTemplate("S")['template'], verbose_name="S", orderable=False, attrs=getChoiceSelectorTemplate("S")['attrs'])
    A = tables2.TemplateColumn(getChoiceSelectorTemplate("A")['template'], verbose_name="A", orderable=False, attrs=getChoiceSelectorTemplate("A")['attrs'])
    T = tables2.TemplateColumn(getChoiceSelectorTemplate("T")['template'], verbose_name="T", orderable=False, attrs=getChoiceSelectorTemplate("T")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class AtlasDiffObjectsTableGoodOptions(AtlasDiffObjectsTable):
    """AtlasDiffObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    P = tables2.TemplateColumn(getChoiceSelectorTemplate("P")['template'], verbose_name="P", orderable=False, attrs=getChoiceSelectorTemplate("P")['attrs'])
    A = tables2.TemplateColumn(getChoiceSelectorTemplate("A")['template'], verbose_name="A", orderable=False, attrs=getChoiceSelectorTemplate("A")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class AtlasDiffObjectsTableFollowupOptions(AtlasDiffObjectsTable):
    """AtlasDiffObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    G = tables2.TemplateColumn(getChoiceSelectorTemplate("G")['template'], verbose_name="G", orderable=False, attrs=getChoiceSelectorTemplate("G")['attrs'])
    P = tables2.TemplateColumn(getChoiceSelectorTemplate("P")['template'], verbose_name="P", orderable=False, attrs=getChoiceSelectorTemplate("P")['attrs'])
    A = tables2.TemplateColumn(getChoiceSelectorTemplate("A")['template'], verbose_name="A", orderable=False, attrs=getChoiceSelectorTemplate("A")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class AtlasDiffObjectsTableGarbageOptions(AtlasDiffObjectsTable):
    """AtlasDiffObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    E = tables2.TemplateColumn(getChoiceSelectorTemplate("E")['template'], verbose_name="E", orderable=False, attrs=getChoiceSelectorTemplate("E")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


AtlasDiffObjectsTables = [AtlasDiffObjectsTableGarbageOptions,
                          AtlasDiffObjectsTableFollowupOptions,
                          AtlasDiffObjectsTableGoodOptions,
                          AtlasDiffObjectsTablePossibleOptions,
                          AtlasDiffObjectsTableEyeballOptions,
                          AtlasDiffObjectsTableAtticOptions,
                          AtlasDiffObjectsTableEyeballOptions,
                          AtlasDiffObjectsTableEyeballOptions,
                          AtlasDiffObjectsTableEyeballOptions,
                          AtlasDiffObjectsTableEyeballOptions,
                          AtlasDiffObjectsTableEyeballOptions,
                          AtlasDiffObjectsTableEyeballOptions]

PROMOTE_DEMOTE = {'C': 1, 'G': 2, 'P': 3, 'E': 4, 'A': 5, 'S': 11, 'T': 0}

# 2015-02-26 KWS Need to hide the current trend and RB Factor from
#                the public pages
class AtlasDiffObjectsTablePublic(AtlasDiffObjectsTable):
    """AtlasDiffObjectsTablePublic.
    """

    current_trend = tables2.Column(accessor='current_trend', verbose_name='Trend', visible=False)
    realbogus_factor = tables2.Column(accessor='realbogus_factor', verbose_name='RB Factor', visible=False)




@login_required
def followupQuickView(request, listNumber):
    """followupQuickView.

    Args:
        request:
        listNumber:
    """
    import sys

    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description

    # We just want to pass the list Id to the HTML page, if it exists
    list_id = None

    try:
        list_id = int(listNumber)
    except ValueError as e:
        pass

    # Since we're using a direct model rather than a database view (hance can't call
    # SELECT database()), I need some way of grabbing the current database name so
    # that we can reference the images correctly.
    public = False
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    # 2017-10-17 KWS Can we filter by object type or filter. Note that there is a
    #                much more elegant (and complex) way of doing this by using
    #                **kwargs, but this also exposes us to injection attacks.
    #                Initial implementation is extremely messy.
    queryFilter = {'detection_list_id': listNumber, 'images_id__isnull': False}

    queryFilter = filterGetParameters(request, queryFilter)


    # 2019-07-31 KWS Add ability to filter on a GW event.
    queryFilterGW = filterGetGWParameters(request, {})

    # 2015-11-17 KWS Get the processing status. If it's not 2, what is it?
    processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
    processingStatus = None
    processingStartTime = None
    if len(processingStatusData) == 1:
        processingStatus = processingStatusData[0].status
        processingStartTime = processingStatusData[0].started

    objectName = None

    # Dummy form search object
    formSearchObject = SearchForObjectForm()

    coneSearchRadius = 3.6
    if request.method == 'POST':
        if 'find_object' in request.POST:
            formSearchObject = SearchForObjectForm(request.POST)
            if formSearchObject.is_valid(): # All validation rules pass
                objectName = formSearchObject.cleaned_data['searchText']
                objectsQueryset = processSearchForm(objectName)
#                if len(objectName) > 0 and objectName != '%%':
#                    objectsQueryset = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & (Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName)))
#                    listHeader = 'Candidates for Followup'
#                else:
#                    objectsQueryset = AtlasDiffObjects.objects.filter(detection_list_id = listNumber, images_id__isnull = False)
            else: # Default query if the form is NOT valid - need to fix!!
                #objectsQueryset = AtlasDiffObjects.objects.filter(detection_list_id = listNumber, images_id__isnull = False)
                # 2019-07-31 KWS Rattle through all the objects to see if we have any
                #                associated with a specified GW event.
                if queryFilterGW:
                    gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=list_id).filter(**queryFilterGW)
                    gwTaggedObjects = [x.transient_object_id_id for x in gw]
                    if len(gwTaggedObjects) == 0:
                        # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
                        gwTaggedObjects = [1]
                    objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter).filter(id__in=gwTaggedObjects)
                else:
                    objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter)
        else:
            # We're using the submit form for the object updates
            if queryFilterGW:
                gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=list_id).filter(**queryFilterGW)
                gwTaggedObjects = [x.transient_object_id_id for x in gw]
                if len(gwTaggedObjects) == 0:
                    # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
                    gwTaggedObjects = [1]
                objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter).filter(id__in=gwTaggedObjects)
            else:
                objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter)

            for key, value in list(request.POST.items()):
                if '_promote_demote' in key and value != 'U':

                    id = int(key.replace('_promote_demote', ''))

                    transient = AtlasDiffObjects.objects.get(pk=id)
                    originallistId = transient.detection_list_id.id

                    # 2017-10-04 KWS Get nearby objects from partner database. If we get a
                    #                named object, don't bother choosing a counter. Just use
                    #                the old name to avoid confusion.
                    xmresults = getNearbyObjectsFromAlternateDatabase(dbName, ALTERNATE_DB_CONNECTIONS, transient, coneSearchRadius)

                    # Override the listId with the value from the form if it exists

                    listId = PROMOTE_DEMOTE[value]
                    if listId < 0:
                        listId = originallistId

                    atlasDesignation = transient.atlas_designation
                    surveyField = transient.survey_field
                    fieldCounter = transient.followup_counter


                    if not atlasDesignation and (listId == GOOD or listId == POSSIBLE or listId == ATTIC or listId == FOLLOWUP):
                        # ASSUMPTION!!  All filenames contain dots and the first part is the field name.
                        surveyField = 'ATLAS'

                        try:
                           fieldCode = SURVEY_FIELDS[surveyField]
                        except KeyError:
                           # Can't find the field, so record the code as 'XX'
                           fieldCode = 'ATLAS'

                        # Let's assume that there's no field counters table.  Let's try and calculate
                        # what the number should be from the data.

                        followupFlagDate = transient.followup_flag_date
                        if followupFlagDate is None:
                           followupFlagDate = datetime.date.today()
                           objectFlagMonth = datetime.date.today().month
                           objectFlagYear = datetime.date.today().year
                        else:
                           objectFlagMonth = followupFlagDate.month
                           objectFlagYear = followupFlagDate.year

                        if xmresults['xmNearestName']:
                            fieldCounter = xmresults['xmNearestCounter']
                            atlasDesignation = xmresults['xmNearestName']
                        else:
#                            fieldCounter = AtlasDiffObjects.objects.filter(followup_flag_date__year = objectFlagYear, survey_field = surveyField, atlas_designation__contains=(objectFlagYear-2000)).aggregate(Max('followup_counter'))['followup_counter__max']
#                            if fieldCounter is None:
#                               # This is the first time we've used the counter
#                               fieldCounter = 1
#                            else:
#                               fieldCounter += 1
#
#                            atlasDesignation = '%s%d%s' % (fieldCode, objectFlagYear - 2000, base26(fieldCounter))

                            nameData = getLocalObjectName(settings.NAMESERVER_API_URL, settings.NAMESERVER_TOKEN, transient.id, transient.ra, transient.dec, followupFlagDate.strftime("%Y-%m-%d"), dbName)
                            if nameData:
                                if nameData['status'] == 201 and nameData['counter'] is not None and nameData['name'] is not None:
                                    sys.stderr.write("\n%s\n" % nameData['info'])
                                    fieldCounter = nameData['counter']
                                    atlasDesignation = nameData['name']
                                else:
                                    sys.stderr.write("\nStatus = %s. %s\n" % (str(nameData['status']), nameData['info']))
                                    request.session['error'] = "ERROR: Nameserver error. Status = %s. %s" % (str(nameData['status']), nameData['info'])
                                    redirect_to = "../../error/"
                                    return HttpResponseRedirect(redirect_to)
                            else:
                                sys.stderr.write("\nBad response from the nameserver. Something went wrong.\n")
                                request.session['error'] = "ERROR: Bad response from the Nameserver."
                                redirect_to = "../../error/"
                                return HttpResponseRedirect(redirect_to)
                    try:
                        # 2011-02-24 KWS Added Observation Status
                        # 2013-10-29 KWS Added date_modified so we can track when bulk updates were done.
                        # 2017-10-17 KWS Who modified the objects?
                        processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
                        if len(processingStatusData) == 1:
                            processingStatus = processingStatusData[0].status
                            processingStartTime = processingStatusData[0].started
                            if processingStatus == 1:
                                request.session['error'] = "WARNING: Database is busy doing a backup. Please come back later."
                                redirect_to = "../../error/"
                                return HttpResponseRedirect(redirect_to)  
                        AtlasDiffObjects.objects.filter(pk=int(key.replace('_promote_demote', ''))).update(detection_list_id = listId,
                                                                                                                   survey_field = surveyField,
                                                                                                               followup_counter = fieldCounter,
                                                                                                              atlas_designation = atlasDesignation,
                                                                                                                     updated_by = request.user.username, 
                                                                                                                  date_modified = datetime.datetime.now()) 
                    except IntegrityError as e:
                        if e[0] == 1062: # Duplicate Key error
                            pass # Do nothing - will eventually raise some errors on the form


    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})

        if queryFilterGW:
            gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=list_id).filter(**queryFilterGW)
            gwTaggedObjects = [x.transient_object_id_id for x in gw]
            if len(gwTaggedObjects) == 0:
                # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
                gwTaggedObjects = [1]
            objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter).filter(id__in=gwTaggedObjects)
        else:
            objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter)

    fgss = False

    # 2017-10-17 default Pages
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    try:
        if int(list_id) in (0,1,2,3,4,5,6,7,8,9,10):
            #table = AtlasDiffObjectsTables[list_id]
            table = AtlasDiffObjectsTables[list_id](objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
        else:
            table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    except ValueError as e:
        table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))


    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = AtlasDiffObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'atlas/followup_quickview_bs.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'list_id': list_id, 'public': public, 'fgss': fgss, 'processingStatus': processingStatus, 'nobjects': nobjects})


# 2013-12-12 KWS Added followupQuickViewAll mainly for the public pages.

@login_required
def followupAllQuickView(request):
    """followupAllQuickView.

    Args:
        request:
    """

    public = False
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    listHeader = None
    objectName = None

    if request.method == 'POST':
        formSearchObject = SearchForObjectForm(request.POST)
        if formSearchObject.is_valid(): # All validation rules pass
            objectName = formSearchObject.cleaned_data['searchText']
            objectsQueryset = processSearchForm(objectName)
#            if len(objectName) > 0 and objectName != '%%':
#                objectsQueryset = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & (Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName)))
#            else:
#                objectsQueryset = AtlasDiffObjects.objects.filter(detection_list_id__id__gt = 0, images_id__isnull = False)

    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})
        else:
            formSearchObject = SearchForObjectForm()

        objectsQueryset = AtlasDiffObjects.objects.filter(detection_list_id__id__gt = 0, images_id__isnull = False)

    fgss = False
    #if objectsQueryset.count() > 0:
    #    table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    #else:
    #    table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = AtlasDiffObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # 2017-10-17 default Pages
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'atlas/followup_quickview_bs.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'public': public, 'fgss': fgss, 'nobjects': nobjects})


@login_required
def followupAllPublicQuickView(request):
    """followupAllPublicQuickView.

    Args:
        request:
    """

    public = True
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    listHeader = None
    objectName = None

    if request.method == 'POST':
        formSearchObject = SearchForObjectForm(request.POST)
        if formSearchObject.is_valid(): # All validation rules pass
            objectName = formSearchObject.cleaned_data['searchText']
            if len(objectName) > 0 and objectName != '%%':
                objectsQueryset = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & (Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName)))
            else:
                objectsQueryset = AtlasDiffObjects.objects.filter(other_designation__isnull = False, detection_list_id__id__gt = 0)

    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})
        else:
            formSearchObject = SearchForObjectForm()

        objectsQueryset = AtlasDiffObjects.objects.filter(other_designation__isnull = False, detection_list_id__id__gt = 0)

    fgss = False
    if objectsQueryset.count() > 0:
        table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    else:
        table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = AtlasDiffObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # 2017-10-17 default Pages
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'atlas/followup_quickview_bs.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'public': public, 'fgss': fgss, 'nobjects': nobjects})


# 2015-03-06 KWS Added new quickview custom lists

@login_required
def userDefinedListsQuickview(request, userDefinedListNumber):
    """userDefinedListsQuickview.

    Args:
        request:
        userDefinedListNumber:
    """

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    public = False
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    objectName = None

    if request.method == 'POST':
        formSearchObject = SearchForObjectForm(request.POST)
        if formSearchObject.is_valid(): # All validation rules pass
            objectName = formSearchObject.cleaned_data['searchText']
            if len(objectName) > 0 and objectName != '%%':
                objectsQueryset = AtlasDiffObjects.objects.filter(Q(atlas_designation__isnull = False) & (Q(atlas_designation__startswith = objectName) | Q(other_designation__startswith = objectName)))
            else:
                objectsQueryset = AtlasDiffObjects.objects.filter(other_designation__isnull = False, detection_list_id__id__gt = 0)

    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})
        else:
            formSearchObject = SearchForObjectForm()

        objectsQueryset = AtlasDiffObjects.objects.filter(tcsobjectgroups__object_group_id=userDefinedListNumber)

    fgss = False
    if objectsQueryset.count() > 0:
        table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    else:
        table = AtlasDiffObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = AtlasDiffObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # 2017-10-17 default Pages
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'atlas/followup_quickview_bs.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'public': public, 'fgss': fgss, 'nobjects': nobjects})


@login_required
def searchResults(request):
    """searchResults.

    Args:
        request:
    """

    from django.db import connection
    import sys

    listHeader = "Search Results"

    results = []
    ddc = True

    public = False
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    if 'atlas3' in dbName:
        ddc = False

    searchText = None
    try:
        searchText = request.session['searchText']
    except KeyError as e:
        searchText = None

    getNonDets = False
    try:
        getNonDets = bool(int(request.GET.get('nondets')))
        request.session['getNonDets'] = getNonDets
    except ValueError as e:
        getNonDets = False
    except TypeError as e:
        getNonDets = False

    getNearbyDets = False
    try:
        getNearbyDets = bool(int(request.GET.get('nearbydets')))
        request.session['getNearbyDets'] = getNearbyDets
    except ValueError as e:
        getNearbyDets = False
    except TypeError as e:
        getNearbyDets = False

    # 2017-10-17 default Pages
    nobjects = 50
    nobjects = request.GET.get('nobjects', '50')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 50

    if request.method == 'POST':
        form = SearchForObjectForm(request.POST)
        if form.is_valid(): # All validation rules pass

            searchText = form.cleaned_data['searchText']
            request.session['searchText'] = searchText
            results = processSearchForm(searchText, getAssociatedData = True, ddc = ddc, getNonDets = getNonDets, getNearbyObjects = getNearbyDets)
    else:
        if searchText:
            form = SearchForObjectForm(initial={'searchText': searchText})
            try:
                # Pick up the non dets variable from the session
                getNonDets = bool(int(request.session['getNonDets']))
            except KeyError as e:
                getNonDets = False

            try:
                # Pick up the nearby dets variable from the session
                getNearbyDets = bool(int(request.session['getNearbyDets']))
            except KeyError as e:
                getNearbyDets = False

            results = processSearchForm(searchText, getAssociatedData = True, ddc = ddc, getNonDets = getNonDets, getNearbyObjects = getNearbyDets)
        else:
            form = SearchForObjectForm()

    paginator = Paginator(results, nobjects)
    page = request.GET.get('page')
    try:
        subdata = paginator.page(page)

    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subdata = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        subdata = paginator.page(paginator.num_pages)

    # 2018-08-07 KWS Added this code so that we ONLY get lightcurves if
    #                the number of objects is less than SHOW_LC_DATA_LIMIT
    if nobjects <= SHOW_LC_DATA_LIMIT:
        for row in subdata:
            # 2018-06-22 KWS Go and get lightcurves of all the objects in the list. This could take a while
            #                NOTE: We should cache the lightcurves in a table, and update them every time
            #                      someone clicks on the candidate page as well as during post ingest cutting.
            lcPoints, lcBlanks, plotLabels, lcLimits = getLCData(row.id, conn = connection, ddc = ddc, getNonDetections = getNonDets)
            row.lc = [lcPoints, lcBlanks, plotLabels]
            row.lcLimits = lcLimits

            # 2018-06-27 KWS Get recurrence plot data. Don't bother with nearest neighbours for the time being.
            detections = AtlasDetectionsddc.objects.filter(atlas_object_id = row.id).filter(deprecated__isnull = True)
            # 2019-11-02 KWS Only use the positive detections by default for the scatter plot data
            recurrences = []
            for d in detections:
                if d.det != 5:
                    recurrences.append({"RA": d.ra, "DEC": d.dec})
            if len(recurrences) == 0:
                recurrences = []
                for d in detections:
                    recurrences.append({"RA": d.ra, "DEC": d.dec})
            recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(recurrences, row.ra, row.dec, objectColour = 20)
            if getNearbyDets:
                xmRecs = getNearbyObjectsForScatterPlot(row.id, row.ra, row.dec, ddc = ddc)
                recurrencePlotData += xmRecs[0]
                recurrencePlotLabels += xmRecs[1]
                averageObjectCoords += xmRecs[2]
                rmsScatter += xmRecs[3]
            row.recurrenceData = [recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter]

            # 2018-08-16 KWS Pick up the Sherlock Crossmatches.
            sxm = SherlockCrossmatches.objects.filter(transient_object_id = row.id).order_by('rank')
            row.sxm = sxm

            # 2021-08-01 KWS Get user comments. We can display these on the quickview page as well.
            comments = TcsObjectComments.objects.filter(transient_object_id = row.id).order_by('date_inserted')
            row.comments = comments

            sc = SherlockClassifications.objects.filter(transient_object_id_id = row.id)
            row.sc = sc


    return render(request, 'atlas/search_results_plotly.html', {'subdata': subdata, 'connection': connection, 'form_searchobject' : form, 'dbname': dbName, 'public': public, 'searchText': searchText, 'nobjects': nobjects, 'showObjectLCThreshold': SHOW_LC_DATA_LIMIT})


# 2018-07-02 KWS New version of the quickview pages, using plotly and bootstrap.
@login_required
def followupQuickViewBootstrapPlotly(request, listNumber):
    """followupQuickViewBootstrapPlotly.

    Args:
        request:
        listNumber:
    """
    from django.db import connection
    import sys

    # 2018-07-05 KWS Pagination loses the rest of the GET parameters. Pass them!
    #                Hideous hack!
    getvars = request.GET.copy()
    urlsuffix=''
    for k,v in list(getvars.items()):
        if k != 'page':
            urlsuffix += "&%s=%s" % (k,v)

    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description

    # We just want to pass the list Id to the HTML page, if it exists
    list_id = None

    try:
        list_id = int(listNumber)
    except ValueError as e:
        pass


    public = False
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

    ddc = True
    if 'atlas3' in dbName:
        ddc = False

    searchText = None
    try:
        searchText = request.session['searchText']
    except KeyError as e:
        searchText = None

    getNonDets = True
    try:
        getNonDets = bool(int(request.GET.get('nondets')))
        request.session['getNonDets'] = getNonDets
    except ValueError as e:
        getNonDets = True
    except TypeError as e:
        getNonDets = True

    getNearbyDets = True
    try:
        getNearbyDets = bool(int(request.GET.get('nearbydets')))
        request.session['getNearbyDets'] = getNearbyDets
    except ValueError as e:
        getNearbyDets = True
    except TypeError as e:
        getNearbyDets = True


    queryFilter = {'detection_list_id': listNumber, 'images_id__isnull': False}
    # 2019-04-16 KWS Get the GW Event name. We will do a "like" query
    #                on this, so we can grab multiple events if necessary.
    queryFilterGW = filterGetGWParameters(request, {})

    queryFilter = filterGetParameters(request, queryFilter)

    # 2017-10-17 default Pages
    nobjects = 50
    nobjects = request.GET.get('nobjects', '50')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 50

    sort = request.GET.get('sort', '-rank').split(',')
    # 2018-07-06 KWS Sometimes the fields don't exist! We don't know this until the
    #                the database generator runs, so the error is difficult to trap.
    #                So go through the sort fields and make sure they're in the model
    #                metadata.  If not, silently default to -rank. In future we'll
    #                direct to an error page with the offending field name(s).
    from django.core.exceptions import FieldDoesNotExist
    for field in sort:
        try: 
            WebViewFollowupTransientsGeneric._meta.get_field(field.replace('-',''))
        except FieldDoesNotExist as e:
            sort = ['-rank']
            break

    # 2015-11-17 KWS Get the processing status. If it's not 2, what is it?
    processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
    processingStatus = None
    processingStartTime = None
    if len(processingStatusData) == 1:
        processingStatus = processingStatusData[0].status
        processingStartTime = processingStatusData[0].started

    objectName = None

    # Dummy form search object
    formSearchObject = SearchForObjectForm()

    coneSearchRadius = 3.6
    if request.method == 'POST':
        if 'find_object' in request.POST:
            formSearchObject = SearchForObjectForm(request.POST)
            if formSearchObject.is_valid(): # All validation rules pass
                objectName = formSearchObject.cleaned_data['searchText']
                results = processSearchForm(objectName)
                if results and type(results[0]) is dict:
                    resultset = []
                    for result in results:
                       resultset.append(Struct(**result))
                    objectsQueryset = resultset
                else:
                    objectsQueryset = results
            else: # Default query if the form is NOT valid - need to fix!!
                #objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter)
                if queryFilterGW:
                    objectsQueryset = []
                    qs = WebViewFollowupTransientsGenericGW.objects.filter(**queryFilter).order_by(*sort)
                    for obj in qs:
                        gw = TcsGravityEventAnnotations.objects.filter(transient_object_id=obj.id).filter(**queryFilterGW)
                        if gw:
                            obj.gw = gw
                            objectsQueryset.append(obj)
                else:
                    objectsQueryset = WebViewFollowupTransientsGeneric.objects.filter(**queryFilter).order_by(*sort)
        else:
            # We're using the submit form for the object updates
            #objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter)
            if queryFilterGW:
                objectsQueryset = []
                qs = WebViewFollowupTransientsGenericGW.objects.filter(**queryFilter).order_by(*sort)
                for obj in qs:
                    gw = TcsGravityEventAnnotations.objects.filter(transient_object_id=obj.id).filter(queryFilterGW)
                    if gw:
                        obj.gw = gw
                        objectsQueryset.append(obj)
            else:
                objectsQueryset = WebViewFollowupTransientsGeneric.objects.filter(**queryFilter).order_by(*sort)


            for key, value in list(request.POST.items()):
                if '_promote_demote' in key and value != 'U':

                    id = int(key.replace('_promote_demote', ''))

                    transient = AtlasDiffObjects.objects.get(pk=id)
                    originallistId = transient.detection_list_id.id

                    # 2017-10-04 KWS Get nearby objects from partner database. If we get a
                    #                named object, don't bother choosing a counter. Just use
                    #                the old name to avoid confusion.
                    xmresults = getNearbyObjectsFromAlternateDatabase(dbName, ALTERNATE_DB_CONNECTIONS, transient, coneSearchRadius)

                    # Override the listId with the value from the form if it exists

                    listId = PROMOTE_DEMOTE[value]
                    if listId < 0:
                        listId = originallistId

                    atlasDesignation = transient.atlas_designation
                    surveyField = transient.survey_field
                    fieldCounter = transient.followup_counter


                    if not atlasDesignation and (listId == GOOD or listId == POSSIBLE or listId == ATTIC or listId == FOLLOWUP):
                        # ASSUMPTION!!  All filenames contain dots and the first part is the field name.
                        surveyField = 'ATLAS'

                        try:
                           fieldCode = SURVEY_FIELDS[surveyField]
                        except KeyError:
                           # Can't find the field, so record the code as 'XX'
                           fieldCode = 'ATLAS'

                        # Let's assume that there's no field counters table.  Let's try and calculate
                        # what the number should be from the data.

                        followupFlagDate = transient.followup_flag_date
                        if followupFlagDate is None:
                           followupFlagDate = datetime.date.today()
                           objectFlagMonth = datetime.date.today().month
                           objectFlagYear = datetime.date.today().year
                        else:
                           objectFlagMonth = followupFlagDate.month
                           objectFlagYear = followupFlagDate.year

                        if xmresults['xmNearestName']:
                            fieldCounter = xmresults['xmNearestCounter']
                            atlasDesignation = xmresults['xmNearestName']
                        else:
#                            fieldCounter = AtlasDiffObjects.objects.filter(followup_flag_date__year = objectFlagYear, survey_field = surveyField, atlas_designation__contains=(objectFlagYear-2000)).aggregate(Max('followup_counter'))['followup_counter__max']
#                            if fieldCounter is None:
#                               # This is the first time we've used the counter
#                               fieldCounter = 1
#                            else:
#                               fieldCounter += 1
#
#                            atlasDesignation = '%s%d%s' % (fieldCode, objectFlagYear - 2000, base26(fieldCounter))

                            nameData = getLocalObjectName(settings.NAMESERVER_API_URL, settings.NAMESERVER_TOKEN, transient.id, transient.ra, transient.dec, followupFlagDate.strftime("%Y-%m-%d"), dbName)
                            if nameData:
                                if nameData['status'] == 201 and nameData['counter'] is not None and nameData['name'] is not None:
                                    sys.stderr.write("\n%s\n" % nameData['info'])
                                    fieldCounter = nameData['counter']
                                    atlasDesignation = nameData['name']
                                else:
                                    sys.stderr.write("\nStatus = %s. %s\n" % (str(nameData['status']), nameData['info']))
                                    request.session['error'] = "ERROR: Nameserver error. Status = %s. %s" % (str(nameData['status']), nameData['info'])
                                    redirect_to = "../../error/"
                                    return HttpResponseRedirect(redirect_to)
                            else:
                                sys.stderr.write("\nBad response from the nameserver. Something went wrong.\n")
                                request.session['error'] = "ERROR: Bad response from the Nameserver."
                                redirect_to = "../../error/"
                                return HttpResponseRedirect(redirect_to)
                    try:
                        # 2011-02-24 KWS Added Observation Status
                        # 2013-10-29 KWS Added date_modified so we can track when bulk updates were done.
                        # 2017-10-17 KWS Who modified the objects?
                        processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
                        if len(processingStatusData) == 1:
                            processingStatus = processingStatusData[0].status
                            processingStartTime = processingStatusData[0].started
                            if processingStatus == 1:
                                request.session['error'] = "WARNING: Database is busy doing a backup. Please come back later."
                                redirect_to = "../../error/"
                                return HttpResponseRedirect(redirect_to)  
                        AtlasDiffObjects.objects.filter(pk=int(key.replace('_promote_demote', ''))).update(detection_list_id = listId,
                                                                                                                   survey_field = surveyField,
                                                                                                               followup_counter = fieldCounter,
                                                                                                              atlas_designation = atlasDesignation,
                                                                                                                     updated_by = request.user.username, 
                                                                                                                  date_modified = datetime.datetime.now()) 
                    except IntegrityError as e:
                        if e[0] == 1062: # Duplicate Key error
                            pass # Do nothing - will eventually raise some errors on the form


    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})

        #objectsQueryset = AtlasDiffObjects.objects.filter(**queryFilter)
        if queryFilterGW:
            objectsQueryset = []
            qs = WebViewFollowupTransientsGenericGW.objects.filter(**queryFilter).order_by(*sort)
            for obj in qs:
                gw = TcsGravityEventAnnotations.objects.filter(transient_object_id=obj.id).filter(**queryFilterGW)
                if gw:
                    obj.gw = gw
                    objectsQueryset.append(obj)
        else:
            objectsQueryset = WebViewFollowupTransientsGeneric.objects.filter(**queryFilter).order_by(*sort)

    # Paginate the results. Completely bypass Django tables.
    paginator = Paginator(objectsQueryset, nobjects)
    page = request.GET.get('page')
    try:
        subdata = paginator.page(page)

    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subdata = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        subdata = paginator.page(paginator.num_pages)

    # Collect the lightcurve and recurrence plot information.  We might want to disable this
    # when collecting information for more than 'n' objects (e.g. 100), since this is very
    # expensive for a browser to render.

    if nobjects <= SHOW_LC_DATA_LIMIT:
        for row in subdata:
            # 2018-06-22 KWS Go and get lightcurves of all the objects in the list. This could take a while
            #                NOTE: We should cache the lightcurves in a table, and update them every time
            #                      someone clicks on the candidate page as well as during post ingest cutting.
            lcPoints, lcBlanks, plotLabels, lcLimits = getLCData(row.id, conn = connection, ddc = ddc, getNonDetections = getNonDets)
            row.lc = [lcPoints, lcBlanks, plotLabels]
            row.lcLimits = lcLimits

            # 2018-06-27 KWS Get recurrence plot data. Don't bother with nearest neighbours for the time being.
            detections = AtlasDetectionsddc.objects.filter(atlas_object_id = row.id).filter(deprecated__isnull = True)
            # 2019-11-02 KWS Only use the positive detections by default for the scatter plot data
            recurrences = []
            for d in detections:
                if d.det != 5:
                    recurrences.append({"RA": d.ra, "DEC": d.dec})
            if len(recurrences) == 0:
                recurrences = []
                for d in detections:
                    recurrences.append({"RA": d.ra, "DEC": d.dec})
            recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(recurrences, row.ra, row.dec, objectColour = 20)
            if getNearbyDets:
                xmRecs = getNearbyObjectsForScatterPlot(row.id, row.ra, row.dec, ddc = ddc)
                recurrencePlotData += xmRecs[0]
                recurrencePlotLabels += xmRecs[1]
                averageObjectCoords += xmRecs[2]
                rmsScatter += xmRecs[3]
            row.recurrenceData = [recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter]

            # 2018-08-16 KWS Pick up the Sherlock Crossmatches.
            sxm = SherlockCrossmatches.objects.filter(transient_object_id = row.id).order_by('rank')
            row.sxm = sxm

            # 2021-08-01 KWS Get user comments. We can display these on the quickview page as well.
            comments = TcsObjectComments.objects.filter(transient_object_id = row.id).order_by('date_inserted')
            row.comments = comments

            sc = SherlockClassifications.objects.filter(transient_object_id_id = row.id)
            row.sc = sc

    return render(request, 'atlas/search_results_plotly.html', {'subdata': subdata, 'listHeader': listHeader, 'form_searchobject' : formSearchObject, 'dbname': dbName, 'list_id': list_id, 'processingStatus': processingStatus, 'nobjects': nobjects, 'public': public, 'searchText': searchText, 'urlsuffix': urlsuffix, 'classifyform': True, 'showObjectLCThreshold': SHOW_LC_DATA_LIMIT })

