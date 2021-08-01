# Create your views here.

#from django.conf.urls.defaults import *
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Avg, Max, Min, Count
from django.db import IntegrityError
from psdb.models import TcsTransientObjects
from psdb.models import TcsTransientReobservations
from psdb.models import TcsPostageStampImages
from psdb.models import TcsClassificationFlags
from psdb.models import TcsDetectionLists
from psdb.models import TcsCrossMatches
from psdb.models import TcsCrossMatchesExternal
from psdb.models import TcsObjectGroups
from psdb.models import TcsObjectGroupDefinitions
from psdb.models import TcsIppToCfaLookup
# 2015-11-17 KWS Added TcsProcessingStatus
from psdb.models import TcsProcessingStatus
from psdb.models import TcsObjectComments
# 2017-03-21 KWS Added TcsGravityEventAnnotations, SherlockClassifications
from psdb.models import TcsGravityEventAnnotations
from psdb.models import SherlockClassifications
from psdb.models import SherlockCrossmatches
from psdb.models import TcsLatestObjectStats
from psdb.models import TcsZooniverseScores
from psdb.dbviews import *
#import django_tables as tables
from django_tables2 import RequestConfig
from django_tables2.utils import A  # alias for Accessor
import django_tables2 as tables2
from math import log
import datetime

from django import forms

# Required for pagination
from django.template import RequestContext

# base 26 numbers for candidate names
from gkutils.commonutils import base26, transform, J2000toGalactic, COORDS_SEX_REGEX_COMPILED, COORDS_DEC_REGEX_COMPILED, NAME_REGEX_COMPILED, coneSearchHTM

# *** FGSS CODE ***
from .catalogueviews import *

# 2011-02-24 KWS Moved all the form choices into a separate file
from psdb.formchoices import *

from django.db.models import Q    # Need Q objects for OR query

# Does an object exist?
from django.core.exceptions import ObjectDoesNotExist

# Lightcurve plotting code
#from plotLightCurve import plotLightCurveFromWeb

# We need to know which database we are talking to for the lightcurves.
from django.conf import settings

# 2012-07-18 KWS Moved all raw lightcurve queries to a dedicated file
from .lightcurvequeries import *

# 2013-02-05 KWS Moved raw lightcurve queries again to a common queries
#                file that can be called by both scripts and Django code.
from .commonqueries import lightcurvePlainQuery, colourDataPlainQuery

# 2016-07-07 KWS Required for authentication
from django.contrib import auth
#from django.core.context_processors import csrf
from django.template.context_processors import csrf

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from psdb.helpers import processSearchForm, sendMessage, filterGetParameters, getDjangoTables2ImageTemplate, SHOW_LC_DATA_LIMIT

class TcsDetectionListsForm(forms.Form):
    """TcsDetectionListsForm.
    """

    name = forms.CharField()

GARBAGE, CONFIRMED, GOOD, POSSIBLE, EYEBALL, ATTIC, ZOO, TBD, FASTEYE = list(range(9))


OBJECT_LISTS = {
    'Garbage': GARBAGE,
    'Confirmed': CONFIRMED,
    'Good': GOOD,
    'Possible': POSSIBLE,
    'Eyeball': EYEBALL,
    'Attic': ATTIC,
    'Zoo': ZOO,
    'Tbd': TBD,
    'FastEye': FASTEYE,
    'DoNothing': -1
}

#SURVEY_FIELDS = {
#    'RINGS': 'P3',
#    'FGSS': '3F',
#    'MD01': '01',
#    'MD02': '02',
#    'MD03': '03',
#    'MD04': '04',
#    'MD05': '05',
#    'MD06': '06',
#    'MD07': '07',
#    'MD08': '08',
#    'MD09': '09',
#    'MD10': '10',
#    'M31': '31',
#}

MONTHS = 'ABCDEFGHIJKL'

ALTERNATE_DB_CONNECTIONS = {'ps1md': ['ps1ss', 'psdb', 'http://star.pst.qub.ac.uk/ps1/psdb/'],
                      'ps1fgss': ['ps1fgssold', 'psdb', 'http://star.pst.qub.ac.uk/ps1fgss/psdb/'],
                      'ps1fgssold': ['ps1fgss', 'psdb2', 'http://star.pst.qub.ac.uk/sne/ps1fgss/psdb/'],
                      'ps1kws': ['ps1ss', 'psdb', 'http://star.pst.qub.ac.uk/ps1/psdb/'],
                      'ps1ss': ['ps1md', 'psdb2', 'http://star.pst.qub.ac.uk/sne/ps1md/psdb/'],
                      'ps1gw': ['ps13pi', 'db0', 'http://star.pst.qub.ac.uk/sne/ps13pi/psdb/'],
                      'pso3': ['ps13pi', 'db0', 'http://star.pst.qub.ac.uk/sne/ps13pi/psdb/'],
                      'ps13pi': ['ps23pi', 'db3', 'http://star.pst.qub.ac.uk/sne/ps23pi/psdb/'],
                      'ps23pi': ['ps13pi', 'db0', 'http://star.pst.qub.ac.uk/sne/ps13pi/psdb/'],
                      'ps2o3': ['pso3', 'db0', 'http://star.pst.qub.ac.uk/sne/pso3/psdb/'],
                      'ps1yse': ['ps13pi', 'db0', 'http://star.pst.qub.ac.uk/sne/ps13pi/psdb/']}

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

LC_LIMITS_ATLAS = {"g": 20.0,
                   "r": 20.0,
                   "i": 20.0,
                   "w": 20.0,
                   "B": 20.0,
                   "V": 20.0}

LC_LIMITS = {'ps1md': LC_LIMITS_MD,
            'ps1ss': LC_LIMITS_MD,
            'ps1kws': LC_LIMITS_MD,
            'ps1fgss': LC_LIMITS_3PI,
            'ps13pi': LC_LIMITS_3PI, 
            'ps13pipublic': LC_LIMITS_3PI,
            'atlas': LC_LIMITS_ATLAS }



# 2016-07-07 KWS Required for authentication
from django.contrib.auth.decorators import login_required

class LoginForm(forms.Form):
    """LoginForm.
    """

    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'30'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'size':'30'}))

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
        # 2017-11-28 KWS Changed login session to 30 days. Too irritating to have to login every day.
        request.session.set_expiry(30 * 86400)
        auth.login(request, user)
        if next == '':
            #return HttpResponseRedirect('../../accounts/loggedin')
            return HttpResponseRedirect('../../')
        else:
            return HttpResponseRedirect(next)

    else:
        return HttpResponseRedirect('../../accounts/invalid')

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




# 2011-02-24 KWS Added drop-down list for observation status
# 2011-04-04 KWS Added drop-down list for User Defined List - populated from the database
class PromoteAndCommentsForm(forms.Form):
    """PromoteAndCommentsForm.
    """

    observation_status = forms.ChoiceField(required=False, label='Spectral Type', widget=forms.Select(attrs={'class':'form-control'}), choices=OBSERVATION_STATUS_CHOICES)
    comments = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'80', 'class':'form-control','placeholder':'Comment','maxlength':'256'}))
    promote_demote = forms.ChoiceField(label='', widget=forms.RadioSelect, choices=PROMOTION_CHOICES)
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


# 2011-08-30 KWS Lightcurve replotting form
class LightCurveModificationForm(forms.Form):
    """LightCurveModificationForm.
    """

    redraw_choice = forms.ChoiceField(label='Replot Choice', widget=forms.RadioSelect, choices=LIGHTCURVE_REPLOTTING_CHOICES)
    minMJD = forms.CharField(label='User Defined Min MJD', required=False, widget=forms.TextInput(attrs={'size':'10'}))
    maxMJD = forms.CharField(label='User Defined Max MJD', required=False, widget=forms.TextInput(attrs={'size':'10'}))


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


# Table to render all table data for an individual candidate.  We need to come back
# to this.  This is actually a union of two tables and VERY slow because it's based
# on a database view.

class WebViewRecurrentObjectsPresentationTable(tables2.Table):
    """WebViewRecurrentObjectsPresentationTable.
    """

    id = tables2.Column(accessor="id", visible=False)
    transient_object_id = tables2.Column(accessor="transient_object_id", visible=False)
    imageid = tables2.Column(verbose_name="Diff ID")
    psf_inst_mag = tables2.Column(verbose_name="Instrument Mag")
    ap_mag = tables2.Column(verbose_name="Aperture Mag")
    cal_psf_mag = tables2.Column(verbose_name="Calibrated Mag")
    mjd_obs = tables2.Column(verbose_name="MJD")
    cmf_file = tables2.Column(verbose_name="CMF File")
    flags = tables2.Column(accessor="flags", visible=False)
    class Meta:
        """Meta.
        """

        model = WebViewRecurrentObjectsPresentation
        template_name = "bootstrap4_django_tables2_atlas.html"


# Experimental code - Use of forms
@login_required
def candidateflot(request, tcs_transient_objects_id):
    """candidateflot.

    Args:
        request:
        tcs_transient_objects_id:
    """

    import sys

    # 2012-03-24 KWS Grab the existing database connection for cone searches.
    #                We could do this the proper 'Django' way, but we would need
    #                models for all the catalogues.  This is not an option in
    #                the short term.  May consider doing it longer term.
    from django.db import connection

    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)

    # 2015-11-17 KWS Get the processing status. If it's not 2, what is it?
    processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
    processingStatus = None
    processingStartTime = None
    if len(processingStatusData) == 1:
        processingStatus = processingStatusData[0].status
        processingStartTime = processingStatusData[0].started

    # 2017-03-21 KWS Get Gravity Wave annotations and Sherlock Classifications
    sc = SherlockClassifications.objects.filter(transient_object_id_id = transient.id)
    sx = SherlockCrossmatches.objects.filter(transient_object_id_id = transient.id)
    gw = TcsGravityEventAnnotations.objects.filter(transient_object_id_id = transient.id).filter(enclosing_contour__lt=100)

    # 2020-02-03 KWS Get citizen scientists that may have classified this object.
    z = None
    try:
        z = TcsZooniverseScores.objects.get(transient_object_id_id = transient.id)
    except ObjectDoesNotExist as e:
        pass

    # 2013-10-30 KWS Get external crossmatches if they exist
    externalXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id = transient.id).exclude(matched_list = 'Transient Name Server').order_by('external_designation')

    # 2019-10-18 KWS Get TNS crossmatch if it exists. Yes - another unnecessary hit to the database, but quick.
    tnsXMs = TcsCrossMatchesExternal.objects.filter(transient_object_id = transient.id, matched_list = 'Transient Name Server')

    existingComments = TcsObjectComments.objects.filter(transient_object_id = transient.id).order_by('date_inserted')

    # 2014-03-11 KWS Pick up any Finder images.

    finderImages = TcsPostageStampImages.objects.filter(image_filename__istartswith = str(transient.id), image_type__iendswith = 'finder')

    # 2013-09-25 KWS Moved the database name to the top of the method so we can call any
    #                that has database name dependencies (e.g. lightcurve limits).
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    # 2013-12-12 KWS Is this a PUBLIC database?
    public = False
    if 'public' in dbName or 'kxws' in dbName:
        public = True

    try:
        detectionLimits = LC_LIMITS[dbName]
    except KeyError as e:
        # Default detections limits for medium deep
        detectionLimits = LC_LIMITS_MD

    lcPoints, lcBlanks, lcNonDetections, followupDetectionData, followupDetectionDataBlanks, plotLabels, lcLimits, colourPlotData, colourPlotLimits, colourPlotLabels = getAllLCData(transient.id, getFollowupData = True, limits = detectionLimits)

    recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(transient.id, transient.ra_psf, transient.dec_psf, objectColour = 20)

    lcData = [lcPoints, lcBlanks, lcNonDetections, followupDetectionData, followupDetectionDataBlanks, plotLabels]
    colourData = [colourPlotData, colourPlotLabels]

    forcedDetectionData = forcedDetectionDataBlanks = plotLabels = plotLimits = forcedDetectionDataFlux = plotLabelsFlux = fluxLimits = colourPlotDataForced = colourPlotLimitsForced = colourPlotLabelsForced = []
    forcedDataList = getForcedLCData(transient.id, getColours = True, limits = detectionLimits)
    if forcedDataList:
       forcedDetectionData, forcedDetectionDataBlanks, plotLabels, plotLimits, forcedDetectionDataFlux, plotLabelsFlux, fluxLimits, colourPlotDataForced, colourPlotLimitsForced, colourPlotLabelsForced = forcedDataList 

    lcDataForced = [forcedDetectionData, forcedDetectionDataBlanks, plotLabels, plotLimits]
    lcDataForcedFlux = [forcedDetectionDataFlux, plotLabelsFlux, fluxLimits]
    colourDataForced = [colourPlotDataForced, colourPlotLimitsForced, colourPlotLabelsForced]

    # 2010-12-02 KWS Get the list ID of the object.  The value of this will determine
    #                which options are presented.
    #                NOTE!! This view will FAIL if presented with a NULL detection list ID.
    detectionList = transient.detection_list_id

    # 2011-04-01 KWS Is this object in a user defined list.  If so, grab the lists so they
    #                can be displayed at the end of the candidate page.  We would also like
    #                to display a checkbox against each list so that the user can remove it
    #                upon page submission.  We would also like select field with the lists
    #                to which this object can be appended (minus the ones for which it is
    #                already a member).

    userListQuerySet = TcsObjectGroups.objects.filter(transient_object_id = transient.id)

    # Grab all the lists of which this object is a member, so that we can exclude these from
    # the user lists to which we want to add this object.
    userListIds = []
    for row in userListQuerySet:
        userListIds.append(row.object_group_id.id)

    listId = None
    if detectionList:
        listId = detectionList.id

    # Dummy form initialisation
    formSearchObject = SearchForObjectForm()

    if request.method == 'POST':
        if 'find_object' in request.POST:
            formSearchObject = SearchForObjectForm(request.POST)
            objectName = formSearchObject.cleaned_data['searchText']
            # Processing is done in the searchResults method
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
#                if len(transient.local_comments) > 0 and len(comments) > 0 and comments not in transient.local_comments:
#                    comments = transient.local_comments + ': ' + comments
#                elif len(comments) == 0 or comments in transient.local_comments:
#                    comments = transient.local_comments

                #listId = transient.detection_list_id.id
                originalListId = transient.detection_list_id.id

                # Override the listId with the value from the form if it exists

                listId = OBJECT_LISTS[choice]
                if listId < 0:
                    listId = transient.detection_list_id.id

                localDesignation = transient.local_designation
                surveyField = transient.survey_field
                fieldCounter = transient.followup_counter

                # 2010-12-02 KWS Added check for localDesignation.  Don't choose a new designation
                # if we already have one.
                if not localDesignation and (listId == GOOD or listId == POSSIBLE or listId == ATTIC or listId == CONFIRMED):
                    # ASSUMPTION!!  All filenames contain dots and the first part is the field name.
                    surveyField = transient.tcs_cmf_metadata_id.filename.split('.')[0].upper()

                    try:
                       fieldCode = settings.SURVEY_FIELDS[surveyField]
                    except KeyError:
                       # Can't find the field, so record the code as 'XX'
                       fieldCode = 'XX'

                    # Let's assume that there's no field counters table.  Let's try and calculate
                    # what the number should be from the data.

                    followupFlagDate = transient.followup_flag_date
                    if followupFlagDate is None:
                       objectFlagMonth = datetime.date.today().month
                       objectFlagYear = datetime.date.today().year
                    else:
                       objectFlagMonth = followupFlagDate.month
                       objectFlagYear = followupFlagDate.year

                    fieldCounter = TcsTransientObjects.objects.filter(followup_flag_date__year = objectFlagYear, survey_field = surveyField).aggregate(Max('followup_counter'))['followup_counter__max']
                    if fieldCounter is None:
                       # This is the first time we've used the counter
                       fieldCounter = 1
                    else:
                       fieldCounter += 1

                    localDesignation = '%d%s%s%s' % (objectFlagYear - 2010, MONTHS[objectFlagMonth - 1], fieldCode, base26(fieldCounter))


                # Do an update if the form is valid, regardless of setting of detection list. If the
                # form is valid, it means we've made a choice - if only to add some comments.
                try:

                   if (originalListId == EYEBALL or originalListId == POSSIBLE or originalListId == ATTIC or originalListId == ZOO or originalListId == TBD or originalListId == FASTEYE) and (listId == GOOD or listId == CONFIRMED):
                       # Is there an object already in the good or confirmed lists within 1.0 arcsec?
                       message, goodObjects = coneSearchHTM(transient.ra_psf, transient.dec_psf, 1.0, 'psdb_web_v_followup_conf_presentation', queryType = FULL, conn = connection, django = True)
                       message, confirmedObjects = coneSearchHTM(transient.ra_psf, transient.dec_psf, 1.0, 'psdb_web_v_followup_good_presentation', queryType = FULL, conn = connection, django = True)
                       if len(goodObjects) > 0 or len(confirmedObjects) > 0:
                           # Object is already in the good or confirmed lists. Please move to attic.
                           request.session['error'] = "WARNING: Duplicate object is already in the Good List. Please go back and move this to the Attic or Garbage."
                           redirect_to = "../../../error/"
                           return HttpResponseRedirect(redirect_to)

                   # 2011-02-24 KWS Added Observation Status
                   # 2013-10-29 KWS Added date_modified so we can track when update were done.
                   TcsTransientObjects.objects.filter(pk=tcs_transient_objects_id).update(detection_list_id = listId,
                                                                                            survey_field = surveyField,
                                                                                        followup_counter = fieldCounter,
                                                                                       local_designation = localDesignation,
                                                                                      observation_status = observationStatus, 
                                                                                           date_modified = datetime.datetime.now()) 

                   if comments:
                       objectComment = TcsObjectComments(transient_object_id_id = transient.id,
                                                                        comment = comments,
                                                                  date_inserted = datetime.datetime.now(),
                                                                       username = request.user.username)

                       objectComment.save()

                   # 2019-08-07 KWS Grab a PS name from the PS nameserver.
                   if listId == GOOD and originalListId != GOOD and (dbName in ('ps13pi', 'pso3', 'ps23pi', 'ps2o3', 'ps1yse')):
                       if settings.DAEMONS['psnames']['test']:
                           response = sendMessage(settings.DAEMONS['psnames']['host'], settings.DAEMONS['psnames']['port'], 'SubmitTest %d' % transient.id)
                       else:
                           response = sendMessage(settings.DAEMONS['psnames']['host'], settings.DAEMONS['psnames']['port'], 'Submit %d' % transient.id)
                       if response:
                           sys.stderr.write('Received %s\n' % repr(response))


                   # 2019-08-07 KWS Register the object on TNS
                   # 2019-08-07 KWS If the previous list was also good (e.g. just adding a comment) don't send a message
                   #                to the TNS daemon. Hard wire the database names so that only the official are allowed
                   #                to request a TNS name.
                   if listId == GOOD and originalListId != GOOD and (dbName in ('ps13pi', 'pso3', 'ps23pi', 'ps2o3', 'ps1yse')):
                       if settings.DAEMONS['tns']['test']:
                           response = sendMessage(settings.DAEMONS['tns']['host'], settings.DAEMONS['tns']['port'], 'SubmitTest %d' % transient.id)
                       else:
                           response = sendMessage(settings.DAEMONS['tns']['host'], settings.DAEMONS['tns']['port'], 'Submit %d' % transient.id)
                       if response:
                           sys.stderr.write('Received %s\n' % repr(response))
                       response = sendMessage(settings.DAEMONS['tns']['host'], settings.DAEMONS['tns']['port'], 'Results')
                       if response:
                           sys.stderr.write('Received %s\n' % repr(response))

                except IntegrityError as e:
                   if e[0] == 1062: # Duplicate Key error
                      pass # Do nothing - will eventually raise some errors on the form

                # 2011-04-05 KWS Insert the new row into the Object Groups table if a user
                #                defined list has been specified.
                # 2015-03-11 KWS Created a new foreign key in TcsObjectGroups so need to alter queries.
                if userDefinedListId > 0:
                    try:
                        userDefinedList = TcsObjectGroupDefinitions.objects.get(pk=userDefinedListId)
                        objGroupId = TcsObjectGroups(transient_object_id=transient, object_group_id=userDefinedList)
                        objGroupId.save()

                    except IntegrityError as e:
                        if e[0] == 1062: # Duplicate Key error
                            pass # Do nothing - it's already in the list (can happen if 2 people modify object at same time)


                # 2011-04-14 KWS Remove the object from any of the groups specified.
                if userListsFromWhichToRemoveObject:
                    for userListId in userListsFromWhichToRemoveObject:
                        userDefinedList = TcsObjectGroupDefinitions.objects.get(pk=userListId)
                        try:
                            objGroupRow = TcsObjectGroups.objects.get(transient_object_id=transient, object_group_id=userDefinedList)
                            if objGroupRow:
                                objGroupRow.delete()

                        except ObjectDoesNotExist as e:
                            # Just in case someone else has already deleted the object before 'Submit' button pressed.
                            pass


                # redirect_to = request.get_full_path()

                # 2010-12-02 KWS Redirect back to the followup page.  Note that if a user has typed
                #            the URL in directly, we should not send them to their previous page, but
                #            instead send them back to the followup page. Note that this assumes a hard
                #            wired /psdb/followup/ URL content. NOTE: We may want to modify this to
                #            include the /psdb/candidate/ URL, so that we can flick from one candidate
                #            to the next without going back to the followup page...

                # 2011-10-26 KWS Added the CfA crossmatching pages to the list of valid URLs
                # 2013-06-27 KWS Added the Quickview pages to the list of valid URLs
                if previousURL and (previousURL.find('/psdb/followup/') >= 0 or previousURL.find('/psdb/userlist/') >= 0 or previousURL.find('/psdb/crossmatch') >= 0 or previousURL.find('/psdb/followup_quickview/') >= 0 or previousURL.find('/psdb/externalcrossmatches/') > 0 or previousURL.find('/psdb/userlist_quickview/') > 0):
                    redirect_to = previousURL
                else:
                    # 2018-02-26 KWS Don't redirect back to list 0 - it takes too long to render
                    if originalListId == 0:
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
        if listId == EYEBALL or listId == FASTEYE or listId == TBD:
            form.fields['promote_demote'].choices = EYEBALL_PROMOTION_CHOICES
        elif listId == CONFIRMED:
            form.fields['promote_demote'].choices = CONFIRMED_POST_PROMOTION_CHOICES
        elif listId == GOOD:
            form.fields['promote_demote'].choices = GOOD_POST_PROMOTION_CHOICES
        elif listId == POSSIBLE:
            form.fields['promote_demote'].choices = POSSIBLE_POST_PROMOTION_CHOICES
        elif listId == ATTIC:
            form.fields['promote_demote'].choices = ATTIC_POST_PROMOTION_CHOICES
        elif listId == ZOO:
            form.fields['promote_demote'].choices = ZOO_POST_PROMOTION_CHOICES
        elif listId == GARBAGE:
            form.fields['promote_demote'].choices = GARBAGE_CHOICES
        else:
            form.fields['promote_demote'].choices = CONFIRMED_POST_PROMOTION_CHOICES

    #cfaMatch = None
    #try:
    #    # Pick up the CfA match if there is one.
    #    cfaMatch = TcsIppToCfaLookup.objects.get(pk=transient.id)
    #except ObjectDoesNotExist, e:
    #    pass

    #transient_images = WebViewPostageStampServerImagesPresentationV2.objects.filter(image_filename__startswith = str(transient.id))
    transient_images = TcsPostageStampImages.objects.filter(image_filename__istartswith = str(transient.id)).exclude(image_filename__istartswith = str(transient.id), image_type__iendswith = 'finder').order_by('-image_filename')

    initial_queryset = WebViewRecurrentObjectsPresentation.objects.filter(transient_object_id = transient.id)
    table = WebViewRecurrentObjectsPresentationTable(initial_queryset, order_by=request.GET.get('sort', '-mjd_obs'))
    RequestConfig(request, paginate=False).configure(table)

    # 2012-05-03 KWS Calculate the average RA and Dec.  Use python rather than the database.

    recurrenceCoords = []

    recurrenceCoords.append([transient.ra_psf, transient.dec_psf])
    for row in initial_queryset:
        recurrenceCoords.append([row.RA, row.DEC])

    raSum = 0
    decSum = 0

    for row in recurrenceCoords:
        raSum += row[0]
        decSum += row[1]

    avgRa = raSum / len(recurrenceCoords)
    avgDec = decSum / len(recurrenceCoords)

    avgRaSex = ra_to_sex(avgRa)
    avgDecSex = dec_to_sex(avgDec)

    # 2019-08-16 KWS Added RA in hours for the wikisky pages.
    avgCoords = {'ra': avgRa, 'dec': avgDec, 'ra_sex': avgRaSex, 'dec_sex': avgDecSex, 'ra_in_hours': ra_in_decimal_hours(avgRa)}

    galactic = transform([avgCoords['ra'], avgCoords['dec']], J2000toGalactic)


    coneSearchRadius = 4.0   # arcsec

    # Grab all objects within 3 arcsec of this one.
    xmList = []
    catalogueName = 'tcs_transient_objects'
    message, xmObjects = coneSearch(transient.ra_psf, transient.dec_psf, coneSearchRadius, catalogueName, queryType = FULL, conn = connection, django = True)

    # The crossmatch Objects xmObjects are a list of two entry lists. The first entry in each row is the separaion.
    # The second entry is the catalogue row dictionary listing the relevant crossmatch.

    if xmObjects:
        numberOfMatches = len(xmObjects)
        # Add the objects into a list of dicts that have consistent names for all catalogues

        for xm in xmObjects:
            # Add to the list all object ids except the current one (which will have
            # a separation of zero).
            if xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]] != transient.id:
                xmList.append({'separation': xm[0], 'xmid': xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]})
                xmid = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]
                xmra = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][1]]
                xmdec = xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][2]]
                xmName = xm[1]["local_designation"]
                if not xmName:
                    xmName = xmid
                xmrecurrencePlotData, xmrecurrencePlotLabels, xmaverageObjectCoords, xmrmsScatter = getRecurrenceDataForPlotting(xmid, transient.ra_psf, transient.dec_psf, secRA = xmra, secDEC = xmdec, secId = xmid, secName = xmName, objectColour = 23)
                recurrencePlotData += xmrecurrencePlotData
                recurrencePlotLabels += xmrecurrencePlotLabels
                averageObjectCoords += xmaverageObjectCoords
                rmsScatter += xmrmsScatter




    # ****************************************************************************************************************
    # 2012-12-10 KWS Dynamic crossmatch against CfA and also old versions of this database (e.g. old FGSS, old MD)
    #                The problem is that we can't re-use the Django connection except for CfA, so will have to do this
    #                using the command line version for old databases.

    # FIRST - get the CfA detections.  Can re-use the connection for that...

    cfaMatch = []
    catalogueName = 'tcs_cfa_detections'
    message, xmObjects = coneSearch(transient.ra_psf, transient.dec_psf, coneSearchRadius, catalogueName, queryType = FULL, conn = connection, django = True)

    if xmObjects:
        # Set cfaMatch to be the nearest match
        # 2013-02-19 KWS Used to send nearest match, but since we've had issues with V2 and V3
        #                tesselation objects, might as well send the whole CfA List
        #cfaMatch = xmObjects[0][1]
        for xm in xmObjects:
            # We need to append the eventID to distinguish between V2 and V3 URLs for CfA.
            cfaMatch.append({'separation': xm[0], 'xmid': xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]], 'eventID': xm[1]['eventID']})

    # NEXT - get the 'old' database detections

    oldDBXmList = []

    oldDBURL = None
    try:
        # HARD WIRED OLD DATABASES DEPEND ON CURRENT DB NAME
        oldDB = ALTERNATE_DB_CONNECTIONS[dbName]
        oldDBURL = oldDB[2]

        # We have to make a manual connection to the database
        try:
            conn = dbConnect(oldDB[1], 'kws', '', oldDB[0], quitOnError = False)

            catalogueName = 'tcs_transient_objects'
            message, xmObjects = coneSearch(transient.ra_psf, transient.dec_psf, coneSearchRadius, catalogueName, queryType = QUICK, conn = conn, django = False)
            conn.close()

            if xmObjects:
                for xm in xmObjects:
                    oldDBXmList.append({'separation': xm[0], 'xmid': xm[1][CAT_ID_RA_DEC_COLS[catalogueName][0][0]]})

        except Exception as e:
            # If for any reason we can't connect to the old database, just continue anyway
            pass

    except KeyError as e:
        # If for any reason we can't find the old database in the dictionary, don't bother doing anything
        pass

    # ****************************************************************************************************************


    # Is this FGSS?  If so pick up the extra Sloan crossmatch data
    if transient.tcs_cmf_metadata_id.filename.split('.')[0].upper() == 'FGSS':
        crossmatches = getSloanCrossmatchData(transient.id)
    else:
        crossmatches = TcsCrossMatches.objects.filter(transient_object_id = transient.id).order_by('separation')

    # Send the recurrence plot data.  Do it here because we may have appended to each list
    # if other objects are nearby.
    recurrenceData = [recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter]

    # 2011-04-04 KWS Add the user defined list to the objects passed to the web page.
    # 2013-10-24 KWS Added context_instance=RequestContext(request) to the render_to_response call.
    #                If not included, the specified template won't understand STATIC_URL.
    return render(request, 'psdb/candidate_plotly.html',{'transient' : transient, 'table' : table, 'images' : transient_images, 'form' : form, 'crossmatches' : crossmatches, 'userList': userListQuerySet, 'cfaMatch': cfaMatch, 'conesearchresults': xmList, 'avg_coords': avgCoords, 'lcdata': lcData, 'lclimits': lcLimits, 'lcdataforced': lcDataForced, 'lcdataforcedflux': lcDataForcedFlux, 'colourdata': colourData, 'colourplotlimits': colourPlotLimits, 'colourdataforced': colourDataForced, 'recurrencedata': recurrenceData, 'conesearchold': oldDBXmList, 'olddburl': oldDBURL, 'externalXMs': externalXMs, 'tnsXMs': tnsXMs, 'public': public, 'form_searchobject': formSearchObject, 'dbName': dbName, 'finderImages': finderImages, 'processingStatus': processingStatus, 'galactic': galactic, 'comments': existingComments, 'sc': sc, 'gw': gw, 'citizens': z, 'sx': sx})



# Plot the extra light curves without cluttering the Candidate page
@login_required
def lightcurves(request, tcs_transient_objects_id):
    """lightcurves.

    Args:
        request:
        tcs_transient_objects_id:
    """

    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
    crossmatches = TcsCrossMatches.objects.filter(transient_object_id = transient.id).order_by('separation')

    # The lightcurve code needs the core database name, not the django one.
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    #dbHost = settings.DATABASE_HOST
    dbHost = settings.DATABASES['default']['HOST']

    if request.method == 'POST':
        form = LightCurveModificationForm(request.POST)
        if form.is_valid(): # All validation rules pass
            # Do stuff here

            choice = int(form.cleaned_data['redraw_choice'])

            if choice > 0:
                # Just assume integers for the MJD
                minMJD = form.cleaned_data['minMJD']
                maxMJD = form.cleaned_data['maxMJD']

                userDefinedMJDLimits = []

                if minMJD and not maxMJD:
                    # The max wasn't defined.  Substitute the special value of -1 into there.
                    try:
                        userDefinedMJDLimits = [int(minMJD), -1]
                    except ValueError as e:
                        userDefinedMJDLimits = []

                elif maxMJD and not minMJD:
                    # The min wasn't defined.  Substitute the special value of -1 into there.
                    try:
                        userDefinedMJDLimits = [-1, int(maxMJD)]
                    except ValueError as e:
                        userDefinedMJDLimits = []
                    
                elif minMJD and maxMJD:
                    try:
                        userDefinedMJDLimits = [int(minMJD), int(maxMJD)]
                    except ValueError as e:
                        userDefinedMJDLimits = []

                # 2012-03-26 KWS Note that we can't re-use the existing DB connection because the cursors are of the wrong type.
                #                (i.e. not DictCursor).  Changing this would require if/else blocks in all SQL code, which is
                #                far too much effort for very little gain.  Note that cone searching (above) is a special case.
                #plotLightCurveFromWeb(dbHost, 'kws', '', dbName, transient.id, plotLimits=choice, userDefinedMJDLimits = userDefinedMJDLimits)

                redirect_to = '../%d/' % transient.id # redirect back to the lightcurve page
                return HttpResponseRedirect(redirect_to)  

    else:
        form = LightCurveModificationForm(initial={'redraw_choice': '0'})


    # 2013-10-24 KWS Added context_instance=RequestContext(request) to the render_to_response call.
    #                If not included, the specified template won't understand STATIC_URL.
    return render(request, 'psdb/lightcurves.html',{'transient' : transient, 'crossmatches' : crossmatches, 'form' : form })


# 2011-07-06 KWS Add facility to write lightcurve numbers in plain text

@login_required
def lightcurveplain(request, tcs_transient_objects_id):
    """lightcurveplain.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
    mjdLimit = 55347.0 # Hard wired to 31st May 2010
    # 2012-07-18 KWS Changed this code to call the custom query from a
    #                dedicated file full of custom queries for lightcurves.
    recurrences = lightcurvePlainQuery(transient.id, mjdLimit = mjdLimit, djangoRawObject = CustomAllObjectOcurrencesPresentation)
    return render(request, 'psdb/lightcurve.txt',{'transient' : transient, 'table' : recurrences }, content_type="text/plain")

# 2013-02-08 KWS As with lightcurves above, make the colour data available via plain text.

@login_required
def colourdataplain(request, tcs_transient_objects_id):
    """colourdataplain.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
    grColour, meangr, grEvolution, riColour, meanri, riEvolution, izColour, meaniz, izEvolution = colourDataPlainQuery(transient.id, applyFudge = True, djangoRawObject = CustomLCPoints)
    colourData = {}
    colourData["gr" ] = grColour
    colourData["grmean" ] = meangr
    colourData["grtrend"] = grEvolution
    colourData["ri" ] = riColour
    colourData["rimean" ] = meanri
    colourData["ritrend"] = riEvolution
    colourData["iz" ] = izColour
    colourData["izmean" ] = meaniz
    colourData["iztrend"] = izEvolution
    return render(request, 'psdb/colourdata.txt',{'transient' : transient, 'colourdata' : colourData }, content_type="text/plain")


# 2015-10-13 KWS Forced photometry plain text query
# @login_required
def lightcurveforcedplain(request, tcs_transient_objects_id):
    """lightcurveforcedplain.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
    mjdLimit = 55347.0 # Hard wired to 31st May 2010
    # 2012-07-18 KWS Changed this code to call the custom query from a
    #                dedicated file full of custom queries for lightcurves.
    recurrences = lightcurveForcedPlainQuery(transient.id, mjdLimit = mjdLimit, djangoRawObject = CustomAllObjectOcurrencesPresentation)
    return render(request, 'psdb/lightcurveforced.txt',{'transient' : transient, 'table' : recurrences }, content_type="text/plain")



@login_required
def obsCatalogue(request, userDefinedListNumber):
    """Create a text only observation catalogue for (e.g.) WHT"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'psdb/obscat.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def obsMediaWiki(request, userDefinedListNumber):
    """Create a text only observation catalogue for (e.g.) WHT"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'psdb/obsmediawiki.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def atelsDiscovery(request, userDefinedListNumber):
    """Create a text only Discovery ATel list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'psdb/atelsdiscovery.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def gcn(request, userDefinedListNumber):
    """Create a text only Discovery ATel list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'psdb/gcn.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


@login_required
def gcnlatex(request, userDefinedListNumber):
    """Create a text only Discovery ATel list"""

    userDefinedListRow = get_object_or_404(TcsObjectGroupDefinitions, pk=userDefinedListNumber)
    listHeader = userDefinedListRow.description

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', 'RA'))

    return render(request, 'psdb/gcn_latex.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")


# 2011-01-21 KWS Completely Revamped the Followup List presentation
# 2013-10-23 KWS Added confidence_factor to the table below


# This class is a generic template for all the prioritised followup transients.
class WebViewFollowupTransientsTable(tables2.Table):
    """WebViewFollowupTransientsTable.
    """

    id = tables2.LinkColumn('candidate', args=[A('id')])
    observation_status = tables2.Column(verbose_name="Spectral Type")
    ps1_designation = tables2.Column(default='', verbose_name="PS1 Name")
    other_designation = tables2.Column(default='', verbose_name="TNS Name")
    local_designation = tables2.Column(default='', verbose_name="Internal Name")

    object_classification = tables2.Column(verbose_name="Machine Classification", visible=False)
    sherlockClassification = tables2.Column(verbose_name='Context Classification')
    catalogue = tables2.Column(visible=False)
    catalogue_object_id = tables2.Column(verbose_name="Nearest Object", visible=False)
    followup_flag_date = tables2.Column(verbose_name="Flag Date")
    separation = tables2.Column(verbose_name="Separation (arcsec)", visible=False)

    rb_cat = tables2.Column(verbose_name="RB Factor (catalogue)")
    rb_pix = tables2.Column(verbose_name="RB Factor (pixels)")
    external_crossmatches = tables2.Column(verbose_name="External Crossmatches")
    discovery_target = tables2.Column(visible=False)
    local_comments = tables2.Column(visible=False)
    xt = tables2.Column(accessor="xt", visible=False)

    class Meta:
        """Meta.
        """

        model = WebViewAbstractFollowup
        template_name = "bootstrap4_django_tables2_atlas.html"


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

    def render_rb_cat(self, value):
        """render_rb_cat.

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

    def render_zooniverse_score(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.2f' % value

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

    def render_earliest_mjd(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.6f' % value

    def render_latest_mjd(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.6f' % value

    def render_earliest_mag(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.2f' % value

    def render_latest_mag(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.2f' % value



followupClassList = [WebViewFollowupTransientsBad,
                     WebViewFollowupTransientsConf,
                     WebViewFollowupTransientsGood,
                     WebViewFollowupTransientsPoss,
                     WebViewFollowupTransientsPend,
                     WebViewFollowupTransientsAttic,
                     WebViewFollowupTransientsZoo,
                     WebViewFollowupTransientsTbd,
                     WebViewFollowupTransientsFast]

@login_required
def followupListNew(request, listNumber):
    """followupListNew.

    Args:
        request:
        listNumber:
    """

    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description

    public = False
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'public' in dbName or 'kxws' in dbName:
        public = True

    objectName = None
    form = SearchForObjectForm()

    if request.method == 'POST':
        form = SearchForObjectForm(request.POST)
        if form.is_valid(): # All validation rules pass
            # Do stuff here
            objectName = form.cleaned_data['searchText']
    else:
        if objectName:
            form = SearchForObjectForm(initial={'searchText': objectName})

    # 2019-07-31 KWS Add ability to filter on a GW event.
    gwEvent = None
    gwEvent = request.GET.get('gwevent')

    # 2019-08-16 KWS Filter on GW event time (currently wired to -10 days, +21 days)
    gwt0 = None
    gwt1 = None

    try:
        gwt0 = float(request.GET.get('gwt0'))
    except ValueError as e:
        gwt0 = None
    except TypeError as e:
        gwt0 = None

    try:
        gwt1 = float(request.GET.get('gwt1'))
    except ValueError as e:
        gwt1 = None
    except TypeError as e:
        gwt1 = None

    if gwEvent:
        gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=listNumber).filter(gravity_event_id__gravity_event_id__contains=gwEvent).filter(enclosing_contour__lt=100)
        gwTaggedObjects = [x.transient_object_id_id for x in gw]
        if len(gwTaggedObjects) == 0:
            # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
            gwTaggedObjects = [1]
        if gwt0 is not None and gwt1 is not None and gwt0 > -10.0 and gwt0 < 21.0 and gwt1 > gwt0 and gwt1 < 21.0:
            initial_queryset = followupClassList[int(listNumber)].objects.filter(ID__in=gwTaggedObjects).filter((Q(earliest_mjd__gt=gwt0) | Q(followup_flag_date__gt=datetime.timedelta(days=gwt0))) & (Q(earliest_mjd__lt=gwt1) | Q(followup_flag_date__lt=datetime.timedelta(days=gwt1))))
        else:
            initial_queryset = followupClassList[int(listNumber)].objects.filter(ID__in=gwTaggedObjects)
    else:
        queryFilter = filterGetParameters(request, {})
        initial_queryset = followupClassList[int(listNumber)].objects.all().filter(**queryFilter)

    table = WebViewFollowupTransientsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'psdb/followup_bs.html', {'table': table, 'rows' : table.rows, 'listHeader' : listHeader, 'form_searchobject' : form, 'public': public})



# 2014-07-23 KWS Added CSV view of the followup lists (so they read by external ingesters)

@login_required
def followupCsv(request, listNumber):
    """Create a text only catalogue of the followup transients"""

    detectionListRow = get_object_or_404(TcsDetectionLists, pk=listNumber)
    listHeader = detectionListRow.description
    initial_queryset = followupClassList[int(listNumber)].objects.all()
    table = WebViewFollowupTransientsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))

    return render(request, 'psdb/followup.txt',{'table': table, 'rows' : table.rows, 'listHeader' : listHeader}, content_type="text/plain")



# 2011-03-18 KWS Experiment to add search form to the Followup Pages

@login_required
def followupAllNew(request):
    """followupAllNew.

    Args:
        request:
    """

    public = False
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'public' in dbName or 'kxws' in dbName:
        public = True

    form = SearchForObjectForm()

    if request.method == 'POST':
        form = SearchForObjectForm(request.POST)
        if form.is_valid(): # All validation rules pass
            # Do stuff here
            objectName = form.cleaned_data['searchText']

    initial_queryset = WebViewFollowupTransients.objects.all()

    table = WebViewFollowupTransientsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'psdb/followup_bs.html', {'table': table, 'rows' : table.rows, 'form_searchobject': form, 'public': public})



# 2014-01-27 KWS Public followup table similar to followupAllNew

class WebViewPublicTransientsTable(tables2.Table):
    """WebViewPublicTransientsTable.
    """

    rank = tables2.Column(accessor="rank", visible=False)
    id = tables2.Column(accessor="ID", visible=False)
    survey_field = tables2.Column(accessor="survey_field", visible=False)
    local_designation = tables2.Column(accessor="local_designation", visible=False)
    observation_status = tables2.Column(verbose_name="Spectral Type")
    object_classification = tables2.Column(verbose_name="Machine Classification")
    sherlockClassification = tables2.Column(verbose_name='Context Classification')
    catalogue_object_id = tables2.Column(verbose_name="Nearest Object")
    followup_flag_date = tables2.Column(verbose_name="Flag Date")
    current_trend = tables2.Column(accessor="current_trend", visible=False)
    separation = tables2.Column(verbose_name="Separation (arcsec)")
    confidence_factor = tables2.Column(accessor="confidence_factor", verbose_name="RB Factor", visible=True)
    external_crossmatches = tables2.Column(verbose_name="External Crossmatches")
    discovery_target = tables2.Column(visible=False)
    class Meta:
        """Meta.
        """

        model = WebViewFollowupTransients


@login_required
def followupAllPublic(request):
    """followupAllPublic.

    Args:
        request:
    """

    public = True
    form = SearchForObjectForm()

    if request.method == 'POST':
        form = SearchForObjectForm(request.POST)
        if form.is_valid(): # All validation rules pass
            # Do stuff here
            objectName = form.cleaned_data['searchText']

    initial_queryset = WebViewFollowupTransients.objects.filter(ps1_designation__isnull = False)

    table = WebViewPublicTransientsTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))

    return render(request, 'psdb/public.html', {'table': table, 'rows' : table.rows, 'form_searchobject' : form, 'public': public})



# 2013-05-28 KWS Added new Followup Quickview (which shows a single row of images)
# 2015-02-18 KWS Added current trend to the quickview list
# 2015-02-35 KWS Added confidence factor (real/bogus) to the quickview list

class TcsTransientObjectsTable(tables2.Table):
    """TcsTransientObjectsTable.
    """

    IMAGE_TEMPLATE = """<img id="stampimages" src="{{ MEDIA_URL }}images/data/{{ dbname }}/{{ record.images_id.whole_mjd }}/{{ record.images_id.%s }}.jpeg" alt="triplet" title="{{ record.images_id.pss_filename }}" onerror="this.src='{{ STATIC_URL }}images/image_not_available.jpeg';" height="300" />""" % 'diff'

    id = tables2.Column(accessor="id", visible=False)
    followup_id = tables2.LinkColumn('candidate', accessor='followup_id', verbose_name="Followup ID", args=[A('id')])
    followup_flag_date = tables2.Column(accessor='followup_flag_date', verbose_name='Flag Date')
    ra_psf = tables2.Column(accessor='ra_psf', verbose_name='RA')
    dec_psf = tables2.Column(accessor='dec_psf', verbose_name='DEC')
    object_classification = tables2.Column(visible=False, accessor='object_classification', verbose_name='Type')
    sherlockClassification = tables2.Column(verbose_name='Context Classification')
    observation_status = tables2.Column(verbose_name="Spec Type")
    other_designation = tables2.Column(accessor='other_designation', verbose_name='TNS Name')
    ps1_designation = tables2.Column(accessor='ps1_designation', verbose_name='PS1 Name')
    local_designation = tables2.Column(accessor='local_designation', verbose_name='Local Name')
    current_trend = tables2.Column(accessor='current_trend', verbose_name='Trend')

    target = tables2.TemplateColumn(getDjangoTables2ImageTemplate('target'), orderable = False)
    ref = tables2.TemplateColumn(getDjangoTables2ImageTemplate('ref'), orderable = False)
    diff = tables2.TemplateColumn(getDjangoTables2ImageTemplate('diff'), orderable = False)

    rb_cat = tables2.Column(accessor='rb_cat', verbose_name='RB Factor (Catalogue)')
    rb_pix = tables2.Column(accessor='rb_pix', verbose_name='RB Factor (Pixel)')
    mjd_obs = tables2.Column(accessor='tcs_images_id__mjd_obs', verbose_name='Recent Triplet MJD', visible = False)
    detection_list_id = tables2.Column(accessor="detection_list_id", visible=False)
    xt = tables2.Column(accessor="xt", visible=False)


    def render_ra_psf(self, value, record):
        """render_ra.

        Args:
            value:
            record:
        """
        ra_in_sex = ra_to_sex (value)
        return ra_in_sex

    def render_dec_psf(self, value, record):
        """render_dec.

        Args:
            value:
            record:
        """
        dec_in_sex = dec_to_sex (value)
        return dec_in_sex

    def render_rb_pix(self, value):
        """render_confidence_factor.

        Args:
            value:
        """
        return '%.3f' % value

    def render_rb_cat(self, value):
        """render_classification_confidence.

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

        model = TcsTransientObjects
        exclude = ['ipp_idet', 'x_psf', 'y_psf', 'x_psf_sig', 'y_psf_sig', 'posangle', 'pltscale', 'psf_inst_mag', 'psf_inst_mag_sig', 'ap_mag', 'ap_mag_radius', 'peak_flux_as_mag', 'cal_psf_mag', 'cal_psf_mag_sig', 'sky', 'sky_sigma', 'psf_chisq', 'cr_nsigma', 'ext_nsigma', 'psf_major', 'psf_minor', 'psf_theta', 'psf_qf', 'psf_ndof', 'psf_npix', 'moments_xx', 'moments_xy', 'moments_yy', 'flags', 'n_frames', 'padding', 'local_comments', 'htm20id', 'htm16id', 'cx', 'cy', 'cz', 'tcs_cmf_metadata_id', 'tcs_images_id', 'date_inserted', 'date_modified', 'followup_priority', 'external_reference_id', 'postage_stamp_request_id', 'image_group_id', 'survey_field', 'followup_counter', 'quality_threshold_pass', 'locally_calculated_mag', 'zoo_request_id', 'psf_inst_flux', 'psf_inst_flux_sig', 'diff_npos', 'diff_fratio', 'diff_nratio_bad', 'diff_nratio_mask', 'diff_nratio_all', 'current_trend', 'processing_flags']
        template_name = "bootstrap4_django_tables2_atlas.html"



class TcsTransientObjectsTableAtticOptions(TcsTransientObjectsTable):
    """TcsTransientObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    P = tables2.TemplateColumn(getChoiceSelectorTemplate("P")['template'], verbose_name="P", orderable=False, attrs=getChoiceSelectorTemplate("P")['attrs'])
    T = tables2.TemplateColumn(getChoiceSelectorTemplate("T")['template'], verbose_name="T", orderable=False, attrs=getChoiceSelectorTemplate("T")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class TcsTransientObjectsTableEyeballOptions(TcsTransientObjectsTable):
    """TcsTransientObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    P = tables2.TemplateColumn(getChoiceSelectorTemplate("P")['template'], verbose_name="P", orderable=False, attrs=getChoiceSelectorTemplate("P")['attrs'])
    A = tables2.TemplateColumn(getChoiceSelectorTemplate("A")['template'], verbose_name="A", orderable=False, attrs=getChoiceSelectorTemplate("A")['attrs'])
    T = tables2.TemplateColumn(getChoiceSelectorTemplate("T")['template'], verbose_name="T", orderable=False, attrs=getChoiceSelectorTemplate("T")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class TcsTransientObjectsTablePossibleOptions(TcsTransientObjectsTable):
    """TcsTransientObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    A = tables2.TemplateColumn(getChoiceSelectorTemplate("A")['template'], verbose_name="A", orderable=False, attrs=getChoiceSelectorTemplate("A")['attrs'])
    T = tables2.TemplateColumn(getChoiceSelectorTemplate("T")['template'], verbose_name="T", orderable=False, attrs=getChoiceSelectorTemplate("T")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class TcsTransientObjectsTableGoodOptions(TcsTransientObjectsTable):
    """TcsTransientObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    C = tables2.TemplateColumn(getChoiceSelectorTemplate("C")['template'], verbose_name="C", orderable=False, attrs=getChoiceSelectorTemplate("C")['attrs'])
    P = tables2.TemplateColumn(getChoiceSelectorTemplate("P")['template'], verbose_name="P", orderable=False, attrs=getChoiceSelectorTemplate("P")['attrs'])
    A = tables2.TemplateColumn(getChoiceSelectorTemplate("A")['template'], verbose_name="A", orderable=False, attrs=getChoiceSelectorTemplate("A")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


class TcsTransientObjectsTableConfirmedOptions(TcsTransientObjectsTable):
    """TcsTransientObjectsTable with buttons (templates in formchoices).
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


class TcsTransientObjectsTableGarbageOptions(TcsTransientObjectsTable):
    """TcsTransientObjectsTable with buttons (templates in formchoices).
    """

    # We want to render the id link as a drop down menu. Do is this way!
    U = tables2.TemplateColumn(getChoiceSelectorTemplate("U", checked = 'checked')['template'], verbose_name="U", orderable=False, attrs=getChoiceSelectorTemplate("U")['attrs'])
    E = tables2.TemplateColumn(getChoiceSelectorTemplate("E")['template'], verbose_name="E", orderable=False, attrs=getChoiceSelectorTemplate("E")['attrs'])

    class Meta:
        """Meta.
        """

        template_name = "bootstrap4_django_tables2_atlas.html"


TcsTransientObjectsTables = [TcsTransientObjectsTableGarbageOptions,
                             TcsTransientObjectsTableConfirmedOptions,
                             TcsTransientObjectsTableGoodOptions,
                             TcsTransientObjectsTablePossibleOptions,
                             TcsTransientObjectsTableEyeballOptions,
                             TcsTransientObjectsTableAtticOptions,
                             TcsTransientObjectsTableEyeballOptions,
                             TcsTransientObjectsTableEyeballOptions,
                             TcsTransientObjectsTableEyeballOptions]






PROMOTE_DEMOTE = {'C': 1, 'G': 2, 'P': 3, 'E': 4, 'A': 5, 'T': 0}

# 2014-02-25 KWS Added a copy of the TcsTransientObjectsTable that hides ref and diff images for FGSS

class TcsTransientObjectsTableFGSS(TcsTransientObjectsTable):
    """TcsTransientObjectsTableFGSS.
    """

    ref = tables2.Column(accessor='tcs_images_id__ref', visible=False)
    diff = tables2.Column(accessor='tcs_images_id__diff', visible=False)

# 2015-02-26 KWS Need to hide the current trend and RB Factor from
#                the public pages
class TcsTransientObjectsTablePublic(TcsTransientObjectsTable):
    """TcsTransientObjectsTablePublic.
    """

    current_trend = tables2.Column(accessor='current_trend', verbose_name='Trend', visible=False)
    confidence_factor = tables2.Column(accessor='confidence_factor', verbose_name='RB Factor', visible=False)




#class ClassifyForm(forms.Form):
#    def __init__(self, table, *args, **kwargs):
#        super(ClassifyForm, self).__init__(*args, **kwargs)
#        # dynamic fields here ...
#        for row in table:
#            self.fields[str(row['id'])] = forms.ChoiceField(label='', widget=forms.RadioSelect, choices=PROMOTION_CHOICES)


@login_required
def followupQuickView(request, listNumber):
    """followupQuickView.

    Args:
        request:
        listNumber:
    """

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
    if 'public' in dbName or 'kxws' in dbName:
        public = True

    # 2015-11-17 KWS Get the processing status. If it's not 2, what is it?
    processingStatusData = TcsProcessingStatus.objects.all().exclude(status = 2)
    processingStatus = None
    processingStartTime = None
    if len(processingStatusData) == 1:
        processingStatus = processingStatusData[0].status
        processingStartTime = processingStatusData[0].started

    objectName = None

    # 2017-10-17 KWS Can we filter by object type or filter. Note that there is a
    #                much more elegant (and complex) way of doing this by using
    #                **kwargs, but this also exposes us to injection attacks.
    #                Initial implementation is extremely messy.

    queryFilter = {'detection_list_id': listNumber, 'tcs_images_id__isnull': False}

    queryFilter = filterGetParameters(request, queryFilter)

    # 2019-07-31 KWS Add ability to filter on a GW event.
    gwEvent = None
    gwEvent = request.GET.get('gwevent')

    # Dummy form initialisation
    formSearchObject = SearchForObjectForm()

    if request.method == 'POST':
        if 'find_object' in request.POST:
            formSearchObject = SearchForObjectForm(request.POST)
            if formSearchObject.is_valid(): # All validation rules pass
                objectName = formSearchObject.cleaned_data['searchText']
            # Processing is done in the searchResults method
        else:
            # We're using the submit form for the object updates
            objectsQueryset = TcsTransientObjects.objects.filter(**queryFilter)

            # 2019-07-31 KWS Rattle through all the objects to see if we have any
            #                associated with a specified GW event.
            if gwEvent:
                gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=list_id).filter(gravity_event_id__gravity_event_id__contains=gwEvent).filter(enclosing_contour__lt=100)
                gwTaggedObjects = [x.transient_object_id_id for x in gw]
                if len(gwTaggedObjects) == 0:
                    # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
                    gwTaggedObjects = [1]
                objectsQueryset = TcsTransientObjects.objects.filter(**queryFilter).filter(id__in=gwTaggedObjects)

            for key, value in list(request.POST.items()):
                if '_promote_demote' in key and value != 'U':

                    id = int(key.replace('_promote_demote', ''))

                    transient = TcsTransientObjects.objects.get(pk=id)
                    originallistId = transient.detection_list_id.id

                    # Override the listId with the value from the form if it exists

                    listId = PROMOTE_DEMOTE[value]
                    if listId < 0:
                        listId = originallistId

                    localDesignation = transient.local_designation
                    surveyField = transient.survey_field
                    fieldCounter = transient.followup_counter


                    if not localDesignation and (listId == GOOD or listId == POSSIBLE or listId == ATTIC or listId == CONFIRMED):
                        # ASSUMPTION!!  All filenames contain dots and the first part is the field name.
                        surveyField = transient.tcs_cmf_metadata_id.filename.split('.')[0].upper()

                        try:
                           fieldCode = settings.SURVEY_FIELDS[surveyField]
                        except KeyError:
                           # Can't find the field, so record the code as 'XX'
                           fieldCode = 'XX'

                        # Let's assume that there's no field counters table.  Let's try and calculate
                        # what the number should be from the data.

                        followupFlagDate = transient.followup_flag_date
                        if followupFlagDate is None:
                           objectFlagMonth = datetime.date.today().month
                           objectFlagYear = datetime.date.today().year
                        else:
                           objectFlagMonth = followupFlagDate.month
                           objectFlagYear = followupFlagDate.year

                        fieldCounter = TcsTransientObjects.objects.filter(followup_flag_date__year = objectFlagYear, survey_field = surveyField).aggregate(Max('followup_counter'))['followup_counter__max']
                        if fieldCounter is None:
                           # This is the first time we've used the counter
                           fieldCounter = 1
                        else:
                           fieldCounter += 1

                        localDesignation = '%d%s%s%s' % (objectFlagYear - 2010, MONTHS[objectFlagMonth - 1], fieldCode, base26(fieldCounter))

                    try:
                        # 2011-02-24 KWS Added Observation Status
                        # 2013-10-29 KWS Added date_modified so we can track when bulk updates were done.
                        TcsTransientObjects.objects.filter(pk=int(key.replace('_promote_demote', ''))).update(detection_list_id = listId,
                                                                                                                   survey_field = surveyField,
                                                                                                               followup_counter = fieldCounter,
                                                                                                              local_designation = localDesignation,
                                                                                                                  date_modified = datetime.datetime.now()) 
                    except IntegrityError as e:
                        if e[0] == 1062: # Duplicate Key error
                            pass # Do nothing - will eventually raise some errors on the form


    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})

        objectsQueryset = TcsTransientObjects.objects.filter(**queryFilter)

        # 2019-07-31 KWS Rattle through all the objects to see if we have any
        #                associated with a specified GW event.
        if gwEvent:
            gw = TcsGravityEventAnnotations.objects.filter(transient_object_id__detection_list_id=list_id).filter(gravity_event_id__gravity_event_id__contains=gwEvent).filter(enclosing_contour__lt=100)
            gwTaggedObjects = [x.transient_object_id_id for x in gw]
            if len(gwTaggedObjects) == 0:
                # Put one fake object in the list. The query will fail with an EmptyResultSet error if we don't.
                gwTaggedObjects = [1]
            objectsQueryset = TcsTransientObjects.objects.filter(**queryFilter).filter(id__in=gwTaggedObjects)

        #formClassifyObject = ClassifyForm(table)

    fgss = False
    import sys
    if objectsQueryset.count() > 0:
        if objectsQueryset[0].tcs_cmf_metadata_id.filename.split('.')[0].upper() == 'FGSS':
            fgss = True
            table = TcsTransientObjectsTableFGSS(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
        else:
            try:
                if int(list_id) in (0,1,2,3,4,5,6,7,8):
                    table = TcsTransientObjectsTables[list_id](objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
                else:
                    table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
            except ValueError as e:
                table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    else:
        table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))


    # 2017-10-17 KWS Give the user control over the number of pages they want to see.
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = TcsTransientObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'psdb/followup_quickview_bs.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'list_id': list_id, 'public': public, 'fgss': fgss, 'processingStatus': processingStatus, 'nobjects': nobjects})


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
    if 'public' in dbName or 'kxws' in dbName:
        public = True

    listHeader = None
    objectName = None

    # Dummy form initialisation
    formSearchObject = SearchForObjectForm()

    if request.method == 'POST':
        formSearchObject = SearchForObjectForm(request.POST)
        if formSearchObject.is_valid(): # All validation rules pass
            objectName = formSearchObject.cleaned_data['searchText']
            if len(objectName) > 0 and objectName != '%%':
                objectsQueryset = TcsTransientObjects.objects.filter(Q(local_designation__isnull = False) & (Q(local_designation__startswith = objectName) | Q(ps1_designation__startswith = objectName)))
            else:
                objectsQueryset = TcsTransientObjects.objects.filter(detection_list_id__id__gt = 0, tcs_images_id__isnull = False)

    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})
        else:
            formSearchObject = SearchForObjectForm()

        objectsQueryset = TcsTransientObjects.objects.filter(detection_list_id__id__gt = 0, tcs_images_id__isnull = False)

    fgss = False
    if objectsQueryset.count() > 0:
        if objectsQueryset[0].tcs_cmf_metadata_id.filename.split('.')[0].upper() == 'FGSS':
            fgss = True
            table = TcsTransientObjectsTableFGSS(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
        else:
            table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    else:
        table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = TcsTransientObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # 2017-10-17 KWS Give the user control over the number of pages they want to see.
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    return render(request, 'psdb/followup_quickview.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'public': public, 'fgss': fgss, 'nobjects': nobjects})


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

    # Dummy form initialisation
    formSearchObject = SearchForObjectForm()

    if request.method == 'POST':
        formSearchObject = SearchForObjectForm(request.POST)
        if formSearchObject.is_valid(): # All validation rules pass
            objectName = formSearchObject.cleaned_data['searchText']
    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})

        objectsQueryset = TcsTransientObjects.objects.filter(ps1_designation__isnull = False, detection_list_id__id__gt = 0)

    fgss = False
    if objectsQueryset.count() > 0:
        if objectsQueryset[0].tcs_cmf_metadata_id.filename.split('.')[0].upper() == 'FGSS':
            fgss = True
            table = TcsTransientObjectsTableFGSS(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
        else:
            table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    else:
        table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = TcsTransientObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # 2017-10-17 KWS Give the user control over the number of pages they want to see.
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    return render(request, 'psdb/followup_quickview.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'public': public, 'fgss': fgss, 'nobjects': nobjects})


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
    if 'public' in dbName or 'kxws' in dbName:
        public = True

    objectName = None

    # Dummy form initialisation
    formSearchObject = SearchForObjectForm()

    if request.method == 'POST':
        formSearchObject = SearchForObjectForm(request.POST)
        if formSearchObject.is_valid(): # All validation rules pass
            objectName = formSearchObject.cleaned_data['searchText']
    else:
        if objectName:
            formSearchObject = SearchForObjectForm(initial={'searchText': objectName})

        objectsQueryset = TcsTransientObjects.objects.filter(tcsobjectgroups__object_group_id=userDefinedListNumber)

    fgss = False
    if objectsQueryset.count() > 0:
        if objectsQueryset[0].tcs_cmf_metadata_id.filename.split('.')[0].upper() == 'FGSS':
            fgss = True
            table = TcsTransientObjectsTableFGSS(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
        else:
            table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))
    else:
        table = TcsTransientObjectsTable(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # Hang on - override the table if the pages are public.
    if public and not fgss:
        table = TcsTransientObjectsTablePublic(objectsQueryset, order_by=request.GET.get('sort', '-followup_id'))

    # 2017-10-17 KWS Give the user control over the number of pages they want to see.
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'psdb/followup_quickview_bs.html', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'form_searchobject': formSearchObject, 'dbname': dbName, 'public': public, 'fgss': fgss, 'nobjects': nobjects})



@login_required
def followupAllPublicTextOnly(request):
    """followupAllPublicTextOnly.

    Args:
        request:
    """

    public = True
    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    listHeader = None
    objectName = None

    objectsQueryset = WebViewFollowupTransients.objects.filter(ps1_designation__isnull = False)
    table = WebViewPublicTransientsTable(objectsQueryset, order_by=request.GET.get('sort', '-rank'))

    return render(request, 'psdb/public_textonly.txt', {'table': table, 'rows': table.rows, 'listHeader': listHeader, 'dbname': dbName, 'public': public}, content_type="text/plain")


# 2011-04-14 KWS User Defined Lists - Very Similar to Followup Transients and re-uses same template.
# 2013-10-23 KWS Added confidence_factor.

class WebViewUserDefinedTable(tables2.Table):
    """WebViewUserDefinedTable.
    """

    id = tables2.LinkColumn('candidate', args=[A('id')])
    observation_status = tables2.Column(verbose_name="Spectral Type")
    ps1_designation = tables2.Column(default='', verbose_name="PS1 Name")
    other_designation = tables2.Column(default='', verbose_name="TNS Name")
    local_designation = tables2.Column(default='', verbose_name="Internal Name")

    object_classification = tables2.Column(verbose_name="Machine Classification", visible=False)
    sherlockClassification = tables2.Column(verbose_name='Context Classification')
    catalogue = tables2.Column(visible=False)
    catalogue_object_id = tables2.Column(verbose_name="Nearest Object", visible=False)
    followup_flag_date = tables2.Column(verbose_name="Flag Date")
    separation = tables2.Column(verbose_name="Separation (arcsec)", visible=False)
    object_group_id = tables2.Column(visible=False)
    #detection_list_id = tables2.Column(verbose_name="List")
    detection_list_id = tables2.Column(accessor='detection_list_id.name', verbose_name="List")

    object_id = tables2.Column(visible=False)
    rb_cat = tables2.Column(verbose_name="RB Factor (catalogue)")
    rb_pix = tables2.Column(verbose_name="RB Factor (pixels)")
    external_crossmatches = tables2.Column(verbose_name="External Crossmatches")
    discovery_target = tables2.Column(visible=False)
    local_comments = tables2.Column(visible=False)
    xt = tables2.Column(visible=False)

    class Meta:
        """Meta.
        """

        model = WebViewUserDefined
        template_name = "bootstrap4_django_tables2_atlas.html"

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

    def render_rb_cat(self, value):
        """render_rb_cat.

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

    def render_zooniverse_score(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.2f' % value

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

    def render_earliest_mjd(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.6f' % value

    def render_latest_mjd(self, value):
        """render_zooniverse_score.

        Args:        
            value:   
        """          
        return '%.6f' % value
                     
    def render_earliest_mag(self, value):
        """render_zooniverse_score.

        Args:
            value:
        """
        return '%.2f' % value

    def render_latest_mag(self, value):
        """render_zooniverse_score.

        Args:        
            value:   
        """
        return '%.2f' % value



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
            objectName = form.cleaned_data['searchText']

    initial_queryset = WebViewUserDefined.objects.filter(object_group_id = userDefinedListNumber)
    table = WebViewUserDefinedTable(initial_queryset, order_by=request.GET.get('sort', '-rank'))
    nobjects = 100
    nobjects = request.GET.get('nobjects', '100')
    try:
        nobjects = int(nobjects)
    except ValueError as e:
        nobjects = 100

    RequestConfig(request, paginate={"per_page": nobjects}).configure(table)

    return render(request, 'psdb/followup_bs.html', {'table': table, 'rows' : table.rows, 'listHeader' : listHeader, 'form_searchobject' : form})


@login_required
# 2019-08-12 KWS Code to generate a JSON table of all the good & confirmed SNe - required by celestial.js
def jsonSNe(request):
    """jsonSNe.

    Args:
        request:
    """
    import json
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    form = SearchForObjectForm()

    querySet = TcsTransientObjects.objects.filter(ps1_designation__isnull = False, detection_list_id__id__gt = 0, detection_list_id__id__lt = 3)
    features = []
    for row in querySet:
        features.append({'type': 'Feature',
                         'id': row.ps1_designation,
                         'properties': {'name': row.ps1_designation,
                                        'mag': '16',
                                        'desig': '',
                                        'con': '',
                                        'sub': 'M31',
                                        'pop': '',
                                        'type': 'dSph',
                                        'dim': '10',
                                        'str': ''},
                         'geometry': {'type': 'Point',
                                      'coordinates':[row.ra_psf, row.dec_psf]}
                         })

    geojson = json.dumps({'type': 'FeatureCollection', 'features': features})

    return render(request, 'psdb/sne.json',{'geojson': geojson}, content_type="text/plain")


@login_required
def homepage2(request):
    """homepage2.

    Args:
        request:
    """
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    form = SearchForObjectForm()

    public = False
    if 'public' in dbName or 'kws' in dbName:
        public = True
        return render(request, 'psdb/index_public.html', {'form_searchobject' : form, 'public': public})
    else:
        return render(request, 'psdb/index_bs_celestial.html', {'form_searchobject' : form, 'public': public})


# 2014-01-31 KWS Altered the home page to only show public info for public database.
@login_required
def homepage(request):
    """homepage.

    Args:
        request:
    """

    #dbName = settings.DATABASE_NAME.replace('_django', '')
    # 2014-10-21 KWS Django > 1.3 settings
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    public = False
    if 'public' in dbName or 'kxws' in dbName:
        public = True
        return render(request, 'psdb/index_public.html', {'public': public})
    else:
        return render(request, 'psdb/index.html', {'public': public})


# 2020-09-30 KWS New error page.
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

    return render(request, 'psdb/error.html', {'error_message': message})


@login_required
def temporaryHomepage(request):
    """temporaryHomepage.

    Args:
        request:
    """
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')

    public = False
    if 'public' in dbName or 'kxws' in dbName:
        public = True
        return render(request, 'psdb/index_public_for_approval.html', {'public': public})
    else:
        return render(request, 'psdb/index.html', {'public': public})


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
    return render(request, 'psdb/reports.html')
    


# DSS2 request image function
@login_required
def dss2(request, tcs_transient_objects_id):
    """dss2.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
    (ra_sex, dec_sex) = coords_dec_to_sex(transient.ra_psf, transient.dec_psf, ' ')
    x = '10'
    y = '10'
    page = getDSS2Image(ra_sex, dec_sex, x, y)
    return render(request, 'psdb/dss2.html', {'page': page})


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


# 2011-04-18 KWS User Defined List Definitions

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
    return render(request, 'psdb/userdefinedlists_bs.html', {'table': table, 'form_searchobject': formSearchObject})


# 2011-10-11 KWS CfA Crossmatching pages

class WebViewCfAtoIPPCrossmatchTable(tables2.Table):
    """WebViewCfAtoIPPCrossmatchTable.
    """

    id = tables2.Column(accessor="ID")
    local_designation = tables2.Column(verbose_name="QUB ID")
    rank = tables2.Column(verbose_name="Rank")
    detection_list_id = tables2.Column(verbose_name="QUB List")
    followup_flag_date = tables2.Column(verbose_name="Flag Date")
    RA = tables2.Column(verbose_name="QUB RA")
    DEC = tables2.Column(verbose_name="QUB DEC")
    field = tables2.Column(verbose_name="MD Field")
    eventID = tables2.Column(verbose_name="CfA Event ID")
    cfa_designation = tables2.Column(verbose_name="CfA Name")
    alertstatus = tables2.Column(verbose_name="CfA Alert List")
    alertDate = tables2.Column(verbose_name="CfA Detection Date")
    raDeg = tables2.Column(verbose_name="CfA RA")
    decDeg = tables2.Column(verbose_name="CfA DEC")
    PS1name = tables2.Column(verbose_name="PS1 Designation")
    separation = tables2.Column(verbose_name="Separation")


    class Meta:
        """Meta.
        """

        model = WebViewCfAToIPPCrossmatch

# New view required to render the table

@login_required
def displayCfAtoIPPCrossmatches(request):
    """displayCfAtoIPPCrossmatches.

    Args:
        request:
    """
    crossmatches = WebViewCfAToIPPCrossmatch.objects.all().order_by('detection_list_id','-rank')
    table = WebViewCfAtoIPPCrossmatchTable(crossmatches, order_by=request.GET.get('sort', '-cfa_designation'))
    crossmatchTitle = 'CfA to IPP Crossmatch'
    return render(request, 'psdb/crossmatch_cfa_with_ipp.html', {'table': table, 'rows' : table.rows, 'crossmatchTitle': crossmatchTitle})

@login_required
def displayIPPtoCfACrossmatches(request):
    """displayIPPtoCfACrossmatches.

    Args:
        request:
    """
    crossmatches = WebViewIPPToCfACrossmatch.objects.all().order_by('detection_list_id','-rank')
    table = WebViewCfAtoIPPCrossmatchTable(crossmatches, order_by=request.GET.get('sort', '-cfa_designation'))
    crossmatchTitle = 'IPP to CfA Crossmatch'
    return render(request, 'psdb/crossmatch_cfa_with_ipp.html', {'table': table, 'rows' : table.rows, 'crossmatchTitle': crossmatchTitle})


class TcsCrossMatchesExternalTable(tables2.Table):
    """TcsCrossMatchesExternalTable.
    """

    id = tables2.Column(accessor="id", visible=False)
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
    transient_object_id__local_designation = tables2.Column(accessor="local_designation", verbose_name="QUB Name")
    transient_object_id__ps1_designation = tables2.Column(accessor="ps1_designation", verbose_name="PS1 Name")
    transient_object_id__detection_list_id = tables2.Column(accessor="detection_list_id", verbose_name="QUB List")
    transient_object_id__ra_psf = tables2.Column(accessor='ra', verbose_name="QUB RA")
    transient_object_id__dec_psf = tables2.Column(accessor='dec', verbose_name="QUB DEC")

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
    table = TcsCrossMatchesExternalTable(crossmatches, order_by=request.GET.get('sort', '-local_designation'))
    crossmatchTitle = 'External Transient Crossmatches'
    return render(request, 'psdb/crossmatch_external.html', {'table': table, 'rows' : table.rows, 'crossmatchTitle': crossmatchTitle})



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

    public = False
    dbName = settings.DATABASES['default']['NAME'].replace('_django', '')
    if 'atlaspublic' in dbName or 'kws' in dbName:
        public = True

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
            #results = processSearchForm(searchText, getAssociatedData = True, ddc = ddc, getNonDets = getNonDets, getNearbyObjects = getNearbyDets)
            results = processSearchForm(searchText, getAssociatedData = True)
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

            #results = processSearchForm(searchText, getAssociatedData = True, ddc = ddc, getNonDets = getNonDets, getNearbyObjects = getNearbyDets)
            results = processSearchForm(searchText, getAssociatedData = True)
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
            #lcPoints, lcBlanks, plotLabels, lcLimits = getLCData(row.id, conn = connection, ddc = ddc, getNonDetections = getNonDets)
            try:
                detectionLimits = LC_LIMITS[dbName]
            except KeyError as e:
                # Default detections limits for medium deep
                detectionLimits = LC_LIMITS_MD

            lcPoints, lcBlanks, lcNonDetections, followupDetectionData, followupDetectionDataBlanks, plotLabels, lcLimits, colourPlotData, colourPlotLimits, colourPlotLabels = getAllLCData(row.id, getFollowupData = True, limits = detectionLimits)
            row.lc = [lcPoints, lcBlanks, plotLabels]
            row.lcLimits = lcLimits

            #recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(recurrences, row.ra, row.dec, objectColour = 20)
            recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(row.id, row.ra_psf, row.dec_psf, objectColour = 20)
            if getNearbyDets:
                xmRecs = getNearbyObjectsForScatterPlot(row.id, row.ra_psf, row.dec_psf)
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


    return render(request, 'psdb/search_results_plotly.html', {'subdata': subdata, 'connection': connection, 'form_searchobject' : form, 'dbname': dbName, 'public': public, 'searchText': searchText, 'nobjects': nobjects, 'showObjectLCThreshold': SHOW_LC_DATA_LIMIT})




@login_required
def astronote(request, tcs_transient_objects_id):
    """astronote.

    Args:
        request:
        tcs_transient_objects_id:
    """
    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)

    # By default, grab the information out of the top sherlock_crossmatch. But allow an offset in case sherlock as zoomed in
    # on the wrong host.
    offset = request.GET.get('offset')
    if not offset:
        offset = 0
    else:
        offset = int(offset)

    transient = get_object_or_404(TcsTransientObjects, pk=tcs_transient_objects_id)
    #lcPoints, lcBlanks, lcNonDetections, followupDetectionData, followupDetectionDataBlanks, plotLabels, lcLimits, colourPlotData, colourPlotLimits, colourPlotLabels = getAllLCData(transient.id, getFollowupData = True, limits = detectionLimits)

    #recurrencePlotData, recurrencePlotLabels, averageObjectCoords, rmsScatter = getRecurrenceDataForPlotting(transient.id, transient.ra_psf, transient.dec_psf, objectColour = 20)

    results = []
    stats = TcsLatestObjectStats.objects.filter(id = transient.id)
    sxms = SherlockCrossmatches.objects.filter(transient_object_id = transient.id).order_by('rank')


    sxm = None
    if len(sxms) > 0 and offset < len(sxms):
        sxm = sxms[offset]

    #return render(request, 'psdb/fasttrackastronote.txt',{'transient': transient, 'sxm': sxm, 'stats': stats}, content_type="text/plain")
    return render(request, 'psdb/fasttrackastronote.txt', {'transient': transient, 'sxm': sxm, 'stats': stats}, content_type="text/plain")
