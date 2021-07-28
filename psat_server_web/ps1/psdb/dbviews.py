from django.db import models
from gkutils.commonutils import *
from math import log10

from psdb.models import TcsCrossMatchesExternal, TcsDetectionLists
import datetime

# Flags dictionary.  Would like to implement this to read the database, but here is a static
# definition in the meantime.
# 2013-02-05 KWS New codes for tidal disruption events, lenses and movers.


GARBAGE, CONFIRMED, GOOD, POSSIBLE, EYEBALL, ATTIC, ZOO = list(range(7))

QUBLists = {
    GARBAGE: 'Garbage',
    CONFIRMED: 'Confirmed',
    GOOD: 'Good',
    POSSIBLE: 'Possible',
    EYEBALL: 'Eyeball',
    ATTIC: 'Attic',
    ZOO: 'Zoo',
    None: None
}


# 2011-01-21 KWS Completely revamped the followup list contents.
# 2013-10-23 KWS Added confidence_factor.
# 2014-02-20 KWS Added external_crossmatches and discovery_target.

class WebViewAbstractFollowup(models.Model):
    """WebViewAbstractFollowup.
    """

    rank = models.IntegerField(db_column='rank')
    id = models.BigIntegerField(primary_key=True, db_column='id')
    survey_field = models.CharField(max_length=255, db_column='survey_field')
    local_designation = models.CharField(max_length=60, db_column='local_designation')
    ps1_designation = models.CharField(max_length=60, db_column='ps1_designation')
    other_designation = models.CharField(max_length=60, db_column='other_designation')
    ra = models.FloatField(db_column='ra_psf')
    dec = models.FloatField(db_column='dec_psf')
    object_classification = models.IntegerField(db_column='object_classification')
    sherlockClassification = models.CharField(max_length=120, db_column='sherlockClassification')
    followup_flag_date = models.DateField(db_column='followup_flag_date')
    observation_status = models.CharField(max_length=40, db_column='observation_status')
    current_trend = models.CharField(max_length=40, db_column='current_trend')
    earliest_mjd = models.FloatField(db_column='earliest_mjd')
    earliest_mag = models.FloatField(db_column='earliest_mag')
    earliest_filter = models.CharField(max_length=80, db_column='earliest_filter')
    latest_mjd = models.FloatField(db_column='latest_mjd')
    latest_mag = models.FloatField(db_column='latest_mag')
    latest_filter = models.CharField(max_length=80, db_column='latest_filter')
    catalogue = models.CharField(max_length=60, db_column='catalogue')
    catalogue_object_id = models.CharField(max_length=30, db_column='catalogue_object_id')
    separation = models.FloatField(db_column='separation')
    rb_cat = models.FloatField(db_column='classification_confidence')
    rb_pix = models.FloatField(db_column='confidence_factor')
    zooniverse_score = models.FloatField(db_column='zooniverse_score')
    external_crossmatches = models.CharField(max_length=1500, db_column='external_crossmatches')
    discovery_target = models.CharField(max_length=90, db_column='discovery_target')

    # 2021-06-09 KWS Added the 'xt' flag (suspected crosstalk)
    xt = models.IntegerField(null=True, blank=True)

    class Meta:
        """Meta.
        """

        abstract = True

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.RA)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.DEC)
        return dec_in_sex

    @property
    def decode_flag_bits(self):
        """decode_flag_bits.
        """
        object_definition = getFlagDefs(self.object_classification, FLAGS, delimiter = ' ')
        return object_definition

    @property
    def externalXMs(self):
        """This is a Hack to get all the external crossmatches per row. Note that
           it only gets executed 100 times (for each page) so it is not disastrous
           for database performance.
        """
        xms = TcsCrossMatchesExternal.objects.filter(transient_object_id__id=self.ID).order_by('external_designation')
        #names = xms.values_list("external_designation", flat=True)
        #nameColumn = ", ".join(names)
        #sys.stderr.write('\nOBJECT (%s) = %s\n' % (self.ID, nameColumn))
        return xms


class WebViewFollowupTransients(WebViewAbstractFollowup):
    """WebViewFollowupTransients.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_all_presentation'
        managed = False

class WebViewFollowupTransientsConf(WebViewAbstractFollowup):
    """WebViewFollowupTransientsConf.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_conf_presentation'
        managed = False

class WebViewFollowupTransientsGood(WebViewAbstractFollowup):
    """WebViewFollowupTransientsGood.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_good_presentation'
        managed = False

class WebViewFollowupTransientsPoss(WebViewAbstractFollowup):
    """WebViewFollowupTransientsPoss.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_poss_presentation'
        managed = False

class WebViewFollowupTransientsBad(WebViewAbstractFollowup):
    """WebViewFollowupTransientsBad.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_bad_presentation'
        managed = False

class WebViewFollowupTransientsPend(WebViewAbstractFollowup):
    """WebViewFollowupTransientsPend.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_pend_presentation'
        managed = False

class WebViewFollowupTransientsAttic(WebViewAbstractFollowup):
    """WebViewFollowupTransientsAttic.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_attic_presentation'
        managed = False

class WebViewFollowupTransientsZoo(WebViewAbstractFollowup):
    """WebViewFollowupTransientsZoo.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_zoo_presentation'
        managed = False

# 2019-07-16 KWS Created two new views - TBD and Fast Track objects. (TBD because
#                I want to keep the Fast Track list = 8 on both ATLAS and Pan-STARRS.

class WebViewFollowupTransientsTbd(WebViewAbstractFollowup):
    """WebViewFollowupTransientsTbd.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_tbd_presentation'
        managed = False

class WebViewFollowupTransientsFast(WebViewAbstractFollowup):
    """WebViewFollowupTransientsFast.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_fast_presentation'
        managed = False


# 2011-04-14 KWS New model for User Defined Lists.
# 2013-10-23 KWS Added confidence_factor.
# 2014-02-20 KWS Added external_crossmatches and discovery_target.

class WebViewAbstractUserDefined(models.Model):
    """WebViewAbstractUserDefined.
    """

    rank = models.IntegerField(db_column='rank')
    id = models.BigIntegerField(db_column='id')
    survey_field = models.CharField(max_length=255, db_column='survey_field')
    local_designation = models.CharField(max_length=60, db_column='local_designation')
    ps1_designation = models.CharField(max_length=60, db_column='ps1_designation')
    other_designation = models.CharField(max_length=60, db_column='other_designation')
    local_comments = models.CharField(max_length=768, db_column='local_comments')
    ra = models.FloatField(db_column='ra_psf')
    dec = models.FloatField(db_column='dec_psf')
    object_classification = models.IntegerField(db_column='object_classification')
    sherlockClassification = models.CharField(max_length=120, db_column='sherlockClassification')
    followup_flag_date = models.DateField(db_column='followup_flag_date')
    observation_status = models.CharField(max_length=40, db_column='observation_status')
    current_trend = models.CharField(max_length=40, db_column='current_trend')
    earliest_mjd = models.FloatField(db_column='earliest_mjd')
    earliest_mag = models.FloatField(db_column='earliest_mag')
    earliest_filter = models.CharField(max_length=80, db_column='earliest_filter')
    latest_mjd = models.FloatField(db_column='latest_mjd')
    latest_mag = models.FloatField(db_column='latest_mag')
    latest_filter = models.CharField(max_length=80, db_column='latest_filter')
    catalogue = models.CharField(max_length=60, db_column='catalogue')
    catalogue_object_id = models.CharField(max_length=30, db_column='catalogue_object_id')
    separation = models.FloatField(db_column='separation')
    # Extra columns for the user defined object list table
    object_group_id = models.IntegerField(db_column='object_group_id')
    detection_list_id = models.ForeignKey(TcsDetectionLists, null=True, to_field='id', db_column='detection_list_id', on_delete=models.CASCADE)
    object_id = models.BigIntegerField(primary_key=True, db_column='object_id')
    rb_cat = models.FloatField(db_column='classification_confidence')
    rb_pix = models.FloatField(db_column='confidence_factor')
    zooniverse_score = models.FloatField(db_column='zooniverse_score')
    external_crossmatches = models.CharField(max_length=1500, db_column='external_crossmatches')
    discovery_target = models.CharField(max_length=90, db_column='discovery_target')

    # 2021-06-09 KWS Added the 'xt' flag (suspected crosstalk)
    xt = models.IntegerField(null=True, blank=True)

    class Meta:
        """Meta.
        """

        abstract = True

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.RA)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.DEC)
        return dec_in_sex

    # 2013-12-20 KWS Added option to grab space-delimited RA and DEC (e.g. for producing catalogues)
    @property
    def ra_sex_spaces(self):
        """ra_sex_spaces.
        """
        ra_in_sex = ra_to_sex (self.RA, delimiter=' ')
        return ra_in_sex

    @property
    def dec_sex_spaces(self):
        """dec_sex_spaces.
        """
        dec_in_sex = dec_to_sex (self.DEC, delimiter=' ')
        return dec_in_sex

    @property
    def decode_flag_bits(self):
        """decode_flag_bits.
        """
        object_definition = getFlagDefs(self.object_classification, FLAGS, delimiter = ' ')
        return object_definition

    @property
    def externalXMs(self):
        """This is a Hack to get all the external crossmatches per row. Note that
           it only gets executed 100 times (for each page) so it is not disastrous
           for database performance.
        """
        xms = TcsCrossMatchesExternal.objects.filter(transient_object_id__id=self.ID).order_by('external_designation')
        #names = xms.values_list("external_designation", flat=True)
        #nameColumn = ", ".join(names)
        #sys.stderr.write('\nOBJECT (%s) = %s\n' % (self.ID, nameColumn))
        return xms

    # 2015-03-13 KWS New methods to retrieve the earliest and latest dates
    #                in date format.
    @property
    def getEarliestDate(self):
        """getEarliestDate.
        """
        dateFraction = getDateFractionMJD(self.earliest_mjd)
        return dateFraction

    @property
    def getLatestDate(self):
        """getLatestDate.
        """
        dateFraction = getDateFractionMJD(self.latest_mjd)
        return dateFraction

class WebViewUserDefined(WebViewAbstractUserDefined):
    """WebViewUserDefined.
    """


    class Meta(WebViewAbstractUserDefined.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_followup_userdefined'
        managed = False



class WebViewRecurrentObjectsPresentation(models.Model):
    """WebViewRecurrentObjectsPresentation.
    """

    id = models.BigIntegerField(primary_key=True, db_column='id')
    transient_object_id = models.BigIntegerField(db_column='transient_object_id')
    imageid = models.IntegerField(db_column='imageid')
    mjd_obs = models.FloatField(db_column='mjd_obs')
    RA = models.FloatField(db_column='ra_psf')
    DEC = models.FloatField(db_column='dec_psf')
    psf_inst_mag = models.FloatField(db_column='psf_inst_mag')
    ap_mag = models.FloatField(db_column='ap_mag')
    cal_psf_mag = models.FloatField(db_column='cal_psf_mag')
    filter = models.CharField(max_length=80, db_column='filter')
    flags = models.IntegerField(db_column='flags')
    cmf_file = models.CharField(max_length=255, db_column='cmf_file')
    image = models.CharField(max_length=255, db_column='name')

    class Meta:
        """Meta.
        """

        db_table = 'psdb_web_v_recurrent_objects_presentation'
        managed = False

    @property
    def flags_bin(self):
       """flags_bin.
       """
       a = bin(int(str(self.flags)),32)
       return a

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.RA)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.DEC)
        return dec_in_sex

class WebViewPostageStampServerImagesPresentation(models.Model):
    """WebViewPostageStampServerImagesPresentation.
    """

    id = models.BigIntegerField(primary_key=True, db_column='id')
    object_id = models.BigIntegerField()
    image_group_id = models.BigIntegerField()
    image_type = models.CharField(max_length=20)
    image_filename = models.CharField(max_length=255)
    pss_filename = models.CharField(max_length=255, blank=True)
    diff_id = models.IntegerField(null=True, blank=True)
    object_mjd = models.FloatField(null=True, blank=True)
    stamp_mjd = models.FloatField(null=True, blank=True)
    pss_error_code = models.IntegerField()
    filename = models.CharField(max_length=255, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'psdb_web_v_postage_stamp_server_images_presentation'
        managed = False

# New version of the Postage Stamp Images presentation
# No object_id, diff_id or object_mjd in this version.
# We could dipense with this altogether, but generating the
# full image filename is easier with the database view.
class WebViewPostageStampServerImagesPresentationV2(models.Model):
    """WebViewPostageStampServerImagesPresentationV2.
    """

    id = models.BigIntegerField(primary_key=True, db_column='id')
    image_group_id = models.BigIntegerField()
    image_type = models.CharField(max_length=20)
    image_filename = models.CharField(max_length=255)
    pss_filename = models.CharField(max_length=255, blank=True)
    stamp_mjd = models.FloatField(null=True, blank=True)
    pss_error_code = models.IntegerField()
    filename = models.CharField(max_length=255, blank=True)
    filter = models.CharField(max_length=80, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'psdb_web_v_postage_stamp_server_images_presentation_v2'
        managed = False

# 2010-01-28 KWS Added new category views that don't commit to a naming scheme.
#                We're just going to have a series of classes that refer to
#                objects by their bitmask categorisation.

# All our views of the different types of objects contain exactly
# the same column names.  Use an Abstract Base Class to define this (and
# any other useful attributes - e.g. magnitude calculations).
# This means that a change of columns only needs to be done once.

class WebViewUniqueAbstractPresentation(models.Model):
    """WebViewUniqueAbstractPresentation.
    """

    ID = models.BigIntegerField(primary_key=True, db_column='id')
    RA = models.FloatField(db_column='ra_psf')
    DEC = models.FloatField(db_column='dec_psf')
    mjd_obs = models.FloatField(db_column='mjd_obs')
    psf_inst_mag = models.FloatField(db_column='psf_inst_mag')
    ap_mag = models.FloatField(db_column='ap_mag')
    cal_psf_mag = models.FloatField(db_column='cal_psf_mag')
    filter = models.CharField(max_length=80, db_column='filter')
    catalogue = models.CharField(max_length=60, db_column='catalogue')
    catalogue_object_id = models.CharField(max_length=30, db_column='catalogue_object_id')
    separation = models.FloatField(db_column='separation')
    image = models.CharField(max_length=255, db_column='target')

    class Meta:
        """Meta.
        """

        abstract = True

    @property
    def flags_bin(self):
       """flags_bin.
       """
       a = bin(int(str(self.flags)),32)
       return a

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.RA)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.DEC)
        return dec_in_sex


class WebViewUnique1Presentation(WebViewUniqueAbstractPresentation):
    """WebViewUnique1Presentation.
    """


    class Meta(WebViewUniqueAbstractPresentation.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_uniq_1_presentation'
        managed = False

class WebViewUnique2Presentation(WebViewUniqueAbstractPresentation):
    """WebViewUnique2Presentation.
    """


    class Meta(WebViewUniqueAbstractPresentation.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_uniq_2_presentation'
        managed = False

class WebViewUnique4Presentation(WebViewUniqueAbstractPresentation):
    """WebViewUnique4Presentation.
    """


    class Meta(WebViewUniqueAbstractPresentation.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_uniq_4_presentation'
        managed = False

class WebViewUnique8Presentation(WebViewUniqueAbstractPresentation):
    """WebViewUnique8Presentation.
    """


    class Meta(WebViewUniqueAbstractPresentation.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_uniq_8_presentation'
        managed = False

class WebViewUnique16Presentation(WebViewUniqueAbstractPresentation):
    """WebViewUnique16Presentation.
    """


    class Meta(WebViewUniqueAbstractPresentation.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_uniq_16_presentation'
        managed = False

class WebViewUnique32Presentation(WebViewUniqueAbstractPresentation):
    """WebViewUnique32Presentation.
    """


    class Meta(WebViewUniqueAbstractPresentation.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_uniq_32_presentation'
        managed = False

class WebViewUnique64Presentation(WebViewUniqueAbstractPresentation):
    """WebViewUnique64Presentation.
    """


    class Meta(WebViewUniqueAbstractPresentation.Meta):
        """Meta.
        """

        db_table = 'psdb_web_v_uniq_64_presentation'
        managed = False

# Add more descendents as more bits (i.e. categories) are used.



# Test of a Custom query.  We'll not associate this class with a
# database table, but execute the query raw in views.py. No inner
# Meta class associated with this class.

# 2015-10-13 KWS Added zero_pt
class CustomAllObjectOcurrencesPresentation(models.Model):
    """CustomAllObjectOcurrencesPresentation.
    """

    id = models.IntegerField(primary_key=True, db_column='id')
    transient_object_id = models.IntegerField(db_column='transient_object_id')
    imageid = models.CharField(max_length=90, db_column='imageid')
    mjd_obs = models.FloatField(db_column='mjd_obs')
    RA = models.FloatField(db_column='ra_psf')
    DEC = models.FloatField(db_column='dec_psf')
    psf_inst_mag = models.FloatField(db_column='psf_inst_mag')
    psf_inst_mag_sig = models.FloatField(db_column='psf_inst_mag_sig')
    ap_mag = models.FloatField(db_column='ap_mag')
    cal_psf_mag = models.FloatField(db_column='cal_psf_mag')
    psf_inst_flux = models.FloatField(db_column='psf_inst_flux')
    psf_inst_flux_sig = models.FloatField(db_column='psf_inst_flux_sig')
    filter = models.CharField(max_length=90, db_column='filter')
    flags = models.CharField(max_length=90, db_column='flags')
    cmf_file = models.CharField(max_length=90, db_column='cmf_file')
    image = models.CharField(max_length=90, db_column='name')
    zero_pt = models.FloatField(db_column='zero_pt')

    @property
    def flags_bin(self):
       """flags_bin.
       """
       a = bin(int(str(self.flags)),32)
       return a

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.RA)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.DEC)
        return dec_in_sex


# 2011-10-11 KWS Added CfA crossmatching views


class WebViewCfAToIPPCrossmatch(models.Model):
    """WebViewCfAToIPPCrossmatch.
    """

    id = models.BigIntegerField(db_column='id')
    local_designation = models.CharField(max_length=60, db_column='local_designation')
    rank = models.IntegerField(db_column='followup_id')
    detection_list_id = models.IntegerField(db_column='detection_list_id')
    followup_flag_date = models.DateField(db_column='followup_flag_date')
    RA = models.FloatField(db_column='ra_psf')
    DEC = models.FloatField(db_column='dec_psf')
    field = models.CharField(max_length=12, db_column='field')
    eventID = models.BigIntegerField(primary_key=True, db_column='eventID')
    cfa_designation = models.CharField(max_length=45, db_column='cfa_designation')
    alertstatus = models.CharField(max_length=36, db_column='alertstatus')
    alertDate = models.CharField(max_length=30, db_column='date')
    raDeg = models.FloatField(db_column='raDeg')
    decDeg = models.FloatField(db_column='decDeg')
    PS1name = models.CharField(max_length=36, db_column='PS1name')
    separation = models.FloatField(db_column='separation')

    class Meta:
        """Meta.
        """

        db_table = 'psdb_web_v_cfa_to_ipp_crossmatch'
        managed = False
 
    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.RA)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.DEC)
        return dec_in_sex

    @property
    def ra_sex_cfa(self):
        """ra_sex_cfa.
        """
        ra_in_sex = ra_to_sex (self.raDeg)
        return ra_in_sex

    @property
    def dec_sex_cfa(self):
        """dec_sex_cfa.
        """
        dec_in_sex = dec_to_sex (self.decDeg)
        return dec_in_sex

    @property
    def cfaDateField(self):
        """cfaDateField.
        """
        year = '20' + self.alertDate[2:4]
        month = self.alertDate[4:6]
        day = self.alertDate[6:8]
        theDate = "%s-%s-%s" % (year, month, day)
        return datetime.datetime.strptime(theDate, '%Y-%m-%d').date()

    @property
    def qubListName(self):
        """qubListName.
        """
        listName = 'Unknown'
        try:
            listName = QUBLists[self.detection_list_id]
        except KeyError:
            # Ignore the problem - just return the 'Unknown' list
            pass
        return listName


class WebViewIPPToCfACrossmatch(models.Model):
    """WebViewIPPToCfACrossmatch.
    """

    id = models.BigIntegerField(primary_key=True, db_column='id')
    local_designation = models.CharField(max_length=60, db_column='local_designation')
    rank = models.IntegerField(db_column='followup_id')
    detection_list_id = models.IntegerField(db_column='detection_list_id')
    followup_flag_date = models.DateField(db_column='followup_flag_date')
    RA = models.FloatField(db_column='ra_psf')
    DEC = models.FloatField(db_column='dec_psf')
    field = models.CharField(max_length=12, db_column='field')
    eventID = models.BigIntegerField(db_column='eventID')
    cfa_designation = models.CharField(max_length=45, db_column='cfa_designation')
    alertstatus = models.CharField(max_length=36, db_column='alertstatus')
    alertDate = models.CharField(max_length=30, db_column='date')
    raDeg = models.FloatField(db_column='raDeg')
    decDeg = models.FloatField(db_column='decDeg')
    PS1name = models.CharField(max_length=36, db_column='PS1name')
    separation = models.FloatField(db_column='separation')

    class Meta:
        """Meta.
        """

        db_table = 'psdb_web_v_ipp_to_cfa_crossmatch'
        managed = False

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.RA)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.DEC)
        return dec_in_sex

    @property
    def ra_sex_cfa(self):
        """ra_sex_cfa.
        """
        ra_in_sex = ra_to_sex (self.raDeg)
        return ra_in_sex

    @property
    def dec_sex_cfa(self):
        """dec_sex_cfa.
        """
        dec_in_sex = dec_to_sex (self.decDeg)
        return dec_in_sex

    @property
    def cfaDateField(self):
        """cfaDateField.
        """
        year = '20' + self.alertDate[2:4]
        month = self.alertDate[4:6]
        day = self.alertDate[6:8]
        theDate = "%s-%s-%s" % (year, month, day)
        return datetime.datetime.strptime(theDate, '%Y-%m-%d').date()

    @property
    def qubListName(self):
        """qubListName.
        """
        listName = 'Unknown'
        try:
            listName = QUBLists[self.detection_list_id]
        except KeyError:
            # Ignore the problem - just return the 'Unknown' list
            pass
        return listName



#+-------------------+----------------------+------+-----+---------+-------+
#| Field             | Type                 | Null | Key | Default | Extra |
#+-------------------+----------------------+------+-----+---------+-------+
#| id                | bigint(20) unsigned  | NO   |     | NULL    |       | 
#| detection_list_id | smallint(5) unsigned | YES  |     | NULL    |       | 
#| ra_psf            | double               | NO   |     | NULL    |       | 
#| dec_psf           | double               | NO   |     | NULL    |       | 
#| field             | varchar(4)           | YES  |     | NULL    |       | 
#| eventID           | int(10) unsigned     | YES  |     | 0       |       | 
#| raDeg             | double               | YES  |     | NULL    |       | 
#| decDeg            | double               | YES  |     | NULL    |       | 
#| alertstatus       | varchar(12)          | YES  |     | NULL    |       | 
#| cfa_designation   | varchar(15)          | YES  |     | NULL    |       | 
#| PS1name           | varchar(12)          | YES  |     | NULL    |       | 
#| separation        | float                | YES  |     | NULL    |       | 
#+-------------------+----------------------+------+-----+---------+-------+


# 2012-07-18 KWS Added two new views for custom lightcurve queries - for Flot.
#                Note that I've added a fake id primary key. You can't run
#                a RAW query without selecting this.
# 2016-11-30 KWS Added zeropoint, deteff_magref, deteff_counts, deteff_calculated_offset
class CustomLCPoints(models.Model):
    """CustomLCPoints.
    """

    id = models.IntegerField(primary_key=True, db_column='id')
    mag = models.FloatField(db_column='mag')
    magerr = models.FloatField(db_column='magerr')
    mjd = models.FloatField(db_column='mjd')
    filter = models.CharField(max_length=90, db_column='filter')
    inst_mag = models.FloatField(db_column='inst_mag')
    exptime = models.FloatField(db_column='exptime')
    zero_pt = models.FloatField(db_column='zero_pt')
    deteff_magref = models.FloatField(db_column='deteff_magref')
    deteff_counts = models.FloatField(db_column='deteff_counts')
    deteff_calculated_offset = models.FloatField(db_column='deteff_calculated_offset')

class CustomLCBlanks(models.Model):
    """CustomLCBlanks.
    """

    id = models.IntegerField(primary_key=True, db_column='id')
    mjd = models.FloatField(db_column='mjd')
    filter = models.CharField(max_length=90, db_column='filter')

# 2012-02-12 KWS Added new raw model for getting followup photometry
class CustomFollowupLCData(models.Model):
    """CustomFollowupLCData.
    """

    id = models.IntegerField(primary_key=True, db_column='id')
    transient_object_id = models.IntegerField(db_column='transient_object_id')
    mjd = models.FloatField(db_column='mjd')
    mag = models.FloatField(db_column='mag')
    magerr = models.FloatField(db_column='magerr')
    filter = models.CharField(max_length=90, db_column='filter')
    telescope_name = models.CharField(max_length=90, db_column='telescope_name')
    telescope_description = models.CharField(max_length=180, db_column='telescope_description')
    instrument_name = models.CharField(max_length=90, db_column='instrument_name')
    instrument_description = models.CharField(max_length=180, db_column='instrument_description')

# 2013-03-07 KWS Added new raw model for grabbing forced photometry
class CustomForcedLCData(models.Model):
    """CustomForcedLCData.
    """

    id = models.IntegerField(primary_key=True, db_column='id')
    transient_object_id = models.IntegerField(db_column='transient_object_id')
    mjd_obs = models.FloatField(db_column='mjd_obs')
    ra_psf = models.FloatField(db_column='ra_psf')
    dec_psf = models.FloatField(db_column='dec_psf')
    skycell = models.CharField(max_length=30, db_column='skycell')
    exptime = models.FloatField(db_column='exptime')
    psf_inst_mag = models.FloatField(db_column='psf_inst_mag')
    psf_inst_mag_sig = models.FloatField(db_column='psf_inst_mag_sig')
    cal_psf_mag = models.FloatField(db_column='cal_psf_mag')
    psf_inst_flux = models.FloatField(db_column='psf_inst_flux')
    psf_inst_flux_sig = models.FloatField(db_column='psf_inst_g_sig')
    filter = models.CharField(max_length=60, db_column='filter')
