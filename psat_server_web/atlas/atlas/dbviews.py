from django.db import models
#from atlas.utils import *
from math import log10

from atlas.models import TcsCrossMatchesExternal, TcsDetectionLists, TcsImages
from gkutils.commonutils import ra_to_sex, dec_to_sex, getFlagDefs, getDateFractionMJD, FLAGS, transform, J2000toGalactic

class CustomLCPoints(models.Model):
    """CustomLCPoints.
    """

    id = models.IntegerField(primary_key=True, db_column='id')
    mag = models.FloatField(db_column='mag')
    magerr = models.FloatField(db_column='magerr')
    mjd = models.FloatField(db_column='mjd')
    exptime = models.FloatField(db_column='exptime')
    filter = models.CharField(max_length=90, db_column='filter')
    zp = models.FloatField(db_column='zp')
    expname = models.CharField(max_length=90, db_column='expname')
    ra = models.FloatField(db_column='ra')
    dec = models.FloatField(db_column='dec')
    atlas_metadata_id = models.IntegerField(db_column='atlas_metadata_id')

class CustomLCBlanks(models.Model):
    """CustomLCBlanks.
    """

    id = models.IntegerField(primary_key=True, db_column='id')
    mjd = models.FloatField(db_column='mjd')
    exptime = models.FloatField(db_column='exptime')
    filter = models.CharField(max_length=90, db_column='filter')
    zp = models.FloatField(db_column='zp')
    expname = models.CharField(max_length=90, db_column='expname')
    filename = models.CharField(max_length=765, db_column='filename')
    input = models.CharField(max_length=765, db_column='input')
    reference = models.CharField(max_length=765, db_column='reference')
    pointing = models.CharField(max_length=765, db_column='pointing')

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

class FollowupRaw(models.Model):
    """FollowupRaw.
    """

    rank = models.IntegerField(db_column='rank')
    id = models.BigIntegerField(primary_key=True, db_column='id')
    atlas_designation = models.CharField(max_length=60, db_column='atlas_designation')
    other_designation = models.CharField(max_length=60, db_column='other_designation')
    ra = models.FloatField(db_column='ra')
    dec = models.FloatField(db_column='dec')
    object_classification = models.IntegerField(db_column='object_classification')
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
    realbogus_factor = models.FloatField(db_column='realbogus_factor')
    zooniverse_score = models.FloatField(db_column='zooniverse_score')
    date_modified = models.FloatField(db_column='date_modified')
    external_crossmatches = models.CharField(max_length=1500, db_column='external_crossmatches')
    discovery_target = models.CharField(max_length=90, db_column='discovery_target')

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.ra)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.dec)
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
        xms = TcsCrossMatchesExternal.objects.filter(transient_object_id__id=self.id).order_by('external_designation')
        #names = xms.values_list("external_designation", flat=True)
        #nameColumn = ", ".join(names)
        return xms



class WebViewAbstractFollowup(models.Model):
    """WebViewAbstractFollowup.
    """

    rank = models.IntegerField(db_column='rank')
    id = models.BigIntegerField(primary_key=True, db_column='id')
    atlas_designation = models.CharField(max_length=60, db_column='atlas_designation')
    other_designation = models.CharField(max_length=60, db_column='other_designation')
    ra = models.FloatField(db_column='ra')
    dec = models.FloatField(db_column='dec')
    ra_avg = models.FloatField(db_column='ra_avg')
    dec_avg = models.FloatField(db_column='dec_avg')
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
    realbogus_factor = models.FloatField(db_column='realbogus_factor')
    zooniverse_score = models.FloatField(db_column='zooniverse_score')
    date_modified = models.FloatField(db_column='date_modified')
    external_crossmatches = models.CharField(max_length=1500, db_column='external_crossmatches')
    discovery_target = models.CharField(max_length=90, db_column='discovery_target')
    rms = models.FloatField(db_column='rms')
    detection_list_id = models.ForeignKey(TcsDetectionLists, null=True, to_field='id', db_column='detection_list_id', on_delete=models.CASCADE)
    images_id = models.ForeignKey(TcsImages, to_field='id', db_column='images_id', on_delete=models.CASCADE)

    class Meta:
        """Meta.
        """

        abstract = True

    @property
    def ra_sex(self):
        """ra_sex.
        """
        if self.ra_avg:
            ra_in_sex = ra_to_sex (self.ra_avg)
        else:
            ra_in_sex = ra_to_sex (self.ra)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        if self.dec_avg:
            dec_in_sex = dec_to_sex (self.dec_avg)
        else:
            dec_in_sex = dec_to_sex (self.dec)
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
        xms = TcsCrossMatchesExternal.objects.filter(transient_object_id__id=self.id).order_by('external_designation')
        #names = xms.values_list("external_designation", flat=True)
        #nameColumn = ", ".join(names)
        #sys.stderr.write('\nOBJECT (%s) = %s\n' % (self.ID, nameColumn))
        return xms

    @property
    def galactic(self):
        """galactic.
        """
        if self.ra_avg and self.dec_avg:
            g = transform([self.ra_avg, self.dec_avg], J2000toGalactic)
        else:
            g = transform([self.ra, self.dec], J2000toGalactic)
        return g


class WebViewFollowupTransients(WebViewAbstractFollowup):
    """WebViewFollowupTransients.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followupall'

class WebViewFollowupTransients0(WebViewAbstractFollowup):
    """WebViewFollowupTransients0.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup0'

class WebViewFollowupTransients1(WebViewAbstractFollowup):
    """WebViewFollowupTransients1.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup1'

class WebViewFollowupTransients2(WebViewAbstractFollowup):
    """WebViewFollowupTransients2.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup2'

class WebViewFollowupTransients3(WebViewAbstractFollowup):
    """WebViewFollowupTransients3.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup3'

class WebViewFollowupTransients4(WebViewAbstractFollowup):
    """WebViewFollowupTransients4.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup4'

class WebViewFollowupTransients5(WebViewAbstractFollowup):
    """WebViewFollowupTransients5.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup5'

class WebViewFollowupTransients6(WebViewAbstractFollowup):
    """WebViewFollowupTransients6.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup6'

class WebViewFollowupTransients7(WebViewAbstractFollowup):
    """WebViewFollowupTransients7.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup7'

class WebViewFollowupTransients8(WebViewAbstractFollowup):
    """WebViewFollowupTransients8.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup8'

class WebViewFollowupTransientsGeneric(WebViewAbstractFollowup):
    """WebViewFollowupTransientsGeneric.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup'

class WebViewFollowupTransientsGenericGW(WebViewAbstractFollowup):
    """WebViewFollowupTransientsGenericGW.
    """


    class Meta(WebViewAbstractFollowup.Meta):
        """Meta.
        """

        db_table = 'atlas_v_followup_gw'


# 2011-04-14 KWS New model for User Defined Lists.
# 2013-10-23 KWS Added confidence_factor.
# 2014-02-20 KWS Added external_crossmatches and discovery_target.

class WebViewAbstractUserDefined(models.Model):
    """WebViewAbstractUserDefined.
    """

    rank = models.IntegerField(db_column='rank')
    id = models.BigIntegerField(db_column='id', primary_key=True)
    atlas_designation = models.CharField(max_length=60, db_column='atlas_designation')
    other_designation = models.CharField(max_length=60, db_column='other_designation')
    local_comments = models.CharField(max_length=768, db_column='local_comments')
    ra = models.FloatField(db_column='ra')
    dec = models.FloatField(db_column='dec')
    ra_avg = models.FloatField(db_column='ra_avg')
    dec_avg = models.FloatField(db_column='dec_avg')
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
    realbogus_factor = models.FloatField(db_column='realbogus_factor')
    zooniverse_score = models.FloatField(db_column='zooniverse_score')
    date_modified = models.DateTimeField(db_column='date_modified')
    external_crossmatches = models.CharField(max_length=1500, db_column='external_crossmatches')
    discovery_target = models.CharField(max_length=90, db_column='discovery_target')
    rms = models.FloatField(db_column='rms')

    class Meta:
        """Meta.
        """

        abstract = True

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.ra)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.dec)
        return dec_in_sex

    # 2013-12-20 KWS Added option to grab space-delimited RA and DEC (e.g. for producing catalogues)
    @property
    def ra_sex_spaces(self):
        """ra_sex_spaces.
        """
        ra_in_sex = ra_to_sex (self.ra, delimiter=' ')
        return ra_in_sex

    @property
    def dec_sex_spaces(self):
        """dec_sex_spaces.
        """
        dec_in_sex = dec_to_sex (self.dec, delimiter=' ')
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
        xms = TcsCrossMatchesExternal.objects.filter(transient_object_id__id=self.id).order_by('external_designation')
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

        db_table = 'atlas_v_followup_userdefined'


# 2018-08-01 KWS Added custom view for getting ATLAS recurrences for PESSTO.
#                This is much faster than the ORM query and doesn't take up
#                all the memory!
class AtlasVRecurrencesddcPessto(models.Model):
    """AtlasVRecurrencesddcPessto.
    """

    rank = models.IntegerField(db_column='rank')
    id = models.BigIntegerField(db_column='id', primary_key=True)
    name = models.CharField(max_length=90, db_column='name')
    tns_name = models.CharField(max_length=90, db_column='tns_name')
    ra = models.FloatField(db_column='ra')
    dec = models.FloatField(db_column='dec')
    expname = models.CharField(max_length=90, db_column='expname')
    mag = models.FloatField(db_column='mag')
    dm = models.FloatField(db_column='dm')
    filter = models.CharField(max_length=90, db_column='filter')
    mjd = models.FloatField(db_column='mjd')

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_v_recurrencesddc_pessto'
