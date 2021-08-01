from django.db import models
from gkutils.commonutils import FLAGS, PROCESSING_FLAGS, getFlagDefs, ra_to_sex, dec_to_sex, getDateFractionMJD
from math import log10
import sys

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

# KWS 2010-01-11 Added Postage Stamp Server database tables and added extra columns to
#                tcs_transient_objects and tcs_transient_reobservations.
# KWS 2010-06-11 Added nine new columns to tcs_transient_objects and eight new columns
#                to tcs_transient_reobservations. Added three new columns to
#                tcs_postage_stamp_images. Added new tcs_zoo_requests table.


# 2014-03-11 KWS Added missing group_type definition. We need this to
#                pick out the finder images.
class TcsImageGroups(models.Model):
    """TcsImageGroups.
    """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    group_type = models.IntegerField()
    class Meta:
        """Meta.
        """

        db_table = 'tcs_image_groups'
        managed = False

# 2014-03-12 KWS Added whole MJD property so we don't have to rely on
#                the django template language to truncate the MJD. Note
#                That we can't use the image MJD, because this might be
#                different from that of the Target MJD.
class TcsPostageStampImages(models.Model):
    """TcsPostageStampImages.
    """

    id = models.BigIntegerField(primary_key=True)
    image_type = models.CharField(max_length=20)
    image_filename = models.CharField(max_length=255)
    pss_filename = models.CharField(max_length=255, blank=True)
    mjd_obs = models.FloatField(null=True, blank=True)
    image_group_id = models.ForeignKey(TcsImageGroups, to_field='id', db_column='image_group_id', on_delete=models.CASCADE)
    pss_error_code = models.IntegerField()
    filter = models.CharField(max_length=80, blank=True)
    mask_ratio = models.FloatField(null=True, blank=True)
    mask_ratio_at_core = models.FloatField(null=True, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_postage_stamp_images'
        managed = False

    @property
    def whole_mjd(self):
       """whole_mjd.
       """
       # The second field is always the target MJD
       fields = self.image_filename.split('_')
       m = int(float(fields[1]))
       return m

    @property
    def f(self):
       """f.
       """
       filterNoZeros = None
       if self.filter:
           filterNoZeros = self.filter[0]
       return filterNoZeros

class TcsPostageStampStatusCodes(models.Model):
    """TcsPostageStampStatusCodes.
    """

    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=80, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_postage_stamp_status_codes'
        managed = False

class TcsDetectionLists(models.Model):
    """TcsDetectionLists.
    """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=80, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_detection_lists'
        managed = False

class TcsPostageStampRequests(models.Model):
    """TcsPostageStampRequests.
    """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    pss_id = models.IntegerField(null=True, blank=True)
    download_attempts = models.IntegerField()
    status = models.ForeignKey(TcsPostageStampStatusCodes, to_field='id', db_column='status', on_delete=models.CASCADE)
    created = models.DateTimeField()
    updated = models.DateTimeField(null=True, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_postage_stamp_requests'
        managed = False

class TcsZooRequests(models.Model):
    """TcsZooRequests.
    """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    zoo_id = models.IntegerField(null=True, blank=True)
    download_attempts = models.IntegerField()
    # Re-use the postage stamp status codes.  No need to create new ones.
    status = models.ForeignKey(TcsPostageStampStatusCodes, to_field='id', db_column='status', on_delete=models.CASCADE)
    created = models.DateTimeField()
    updated = models.DateTimeField(null=True, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_zoo_requests'
        managed = False

class TcsCatalogueTables(models.Model):
    """TcsCatalogueTables.
    """

    id = models.IntegerField(primary_key=True)
    table_name = models.CharField(max_length=30)
    description = models.CharField(max_length=60)
    url = models.CharField(max_length=255, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_catalogue_tables'
        managed = False

    def __unicode__(self):
        """__unicode__.
        """
        return self.table_name

class TcsClassificationFlags(models.Model):
    """TcsClassificationFlags.
    """

    flag_id = models.IntegerField(primary_key=True)
    flag_name = models.CharField(max_length=30)
    description = models.CharField(max_length=80)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_classification_flags'
        managed = False

# 2013-05-29 KWS Repurposed the tcs_images table to refer to a triplet set
#                Also added property to return whole MJD, since there is
#                no template tag to facilitate this (amazingly).

class TcsImages(models.Model):
    """TcsImages.
    """

    id = models.BigIntegerField(primary_key=True)
    target = models.CharField(max_length=255)
    ref = models.CharField(max_length=255)
    diff = models.CharField(max_length=255)
    mjd_obs = models.FloatField(null=True, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_images'
        managed = False

    @property
    def whole_mjd(self):
       """whole_mjd.
       """
       m = int(self.mjd_obs)
       return m


# 2011-04-01 KWS Added two new tables for User Defined Lists of objects

class TcsObjectGroupDefinitions(models.Model):
    """TcsObjectGroupDefinitions.
    """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=80)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_object_group_definitions'
        managed = False


# 2014-01-08 KWS Added tessellation and skycell columns
class TcsCmfMetadata(models.Model):
    """TcsCmfMetadata.
    """

    id = models.BigIntegerField(primary_key=True)
    filename = models.CharField(unique=True, max_length=255, blank=True)
    tessellation = models.CharField(unique=True, max_length=255, blank=True)
    skycell = models.CharField(unique=True, max_length=255, blank=True)
    airmass = models.FloatField(null=True, blank=True)
    angle = models.FloatField(null=True, blank=True)
    cell_bad = models.FloatField(null=True, blank=True)
    cell_biassec = models.CharField(max_length=80, blank=True)
    cell_darktime = models.FloatField(null=True, blank=True)
    cell_gain = models.FloatField(null=True, blank=True)
    cell_readnoise = models.FloatField(null=True, blank=True)
    cell_saturation = models.FloatField(null=True, blank=True)
    cell_trimsec = models.CharField(max_length=80, blank=True)
    cell_varfactor = models.FloatField(null=True, blank=True)
    cell_xbin = models.IntegerField(null=True, blank=True)
    cell_xsize = models.IntegerField(null=True, blank=True)
    cell_xwindow = models.IntegerField(null=True, blank=True)
    cell_ybin = models.IntegerField(null=True, blank=True)
    cell_ysize = models.IntegerField(null=True, blank=True)
    cell_ywindow = models.IntegerField(null=True, blank=True)
    chip_id = models.CharField(max_length=80, blank=True)
    chip_temp = models.CharField(max_length=80, blank=True)
    chip_xsize = models.IntegerField(null=True, blank=True)
    chip_ysize = models.IntegerField(null=True, blank=True)
    dt_phot = models.FloatField(null=True, blank=True)
    exptime = models.FloatField(null=True, blank=True)
    extdata = models.CharField(max_length=80, blank=True)
    exttype = models.CharField(max_length=80, blank=True)
    flimit = models.FloatField(null=True, blank=True)
    fpa_alt = models.FloatField(null=True, blank=True)
    fpa_az = models.FloatField(null=True, blank=True)
    fpa_comment = models.CharField(max_length=80, blank=True)
    fpa_dec = models.CharField(max_length=80, blank=True)
    fpa_detector = models.CharField(max_length=80, blank=True)
    fpa_elevation = models.FloatField(null=True, blank=True)
    fpa_env_dir = models.FloatField(null=True, blank=True)
    fpa_env_humid = models.FloatField(null=True, blank=True)
    fpa_env_temp = models.FloatField(null=True, blank=True)
    fpa_env_wind = models.FloatField(null=True, blank=True)
    fpa_filterid = models.CharField(max_length=80, blank=True)
    fpa_filter = models.CharField(max_length=80, blank=True)
    fpa_focus = models.FloatField(null=True, blank=True)
    fpa_instrument = models.CharField(max_length=80, blank=True)
    fpa_latitude = models.CharField(max_length=80, blank=True)
    fpa_longitude = models.CharField(max_length=80, blank=True)
    fpa_m1tilt = models.FloatField(null=True, blank=True)
    fpa_m1tip = models.FloatField(null=True, blank=True)
    fpa_m1x = models.FloatField(null=True, blank=True)
    fpa_m1y = models.FloatField(null=True, blank=True)
    fpa_m1z = models.FloatField(null=True, blank=True)
    fpa_m2tilt = models.FloatField(null=True, blank=True)
    fpa_m2tip = models.FloatField(null=True, blank=True)
    fpa_m2x = models.FloatField(null=True, blank=True)
    fpa_m2y = models.FloatField(null=True, blank=True)
    fpa_m2z = models.FloatField(null=True, blank=True)
    fpa_object = models.CharField(max_length=80, blank=True)
    fpa_obs_group = models.CharField(max_length=80, blank=True)
    fpa_obs_mode = models.CharField(max_length=80, blank=True)
    fpa_obstype = models.CharField(max_length=80, blank=True)
    fpa_obs = models.CharField(max_length=80, blank=True)
    fpa_pon_time = models.FloatField(null=True, blank=True)
    fpa_posangle = models.FloatField(null=True, blank=True)
    fpa_radecsys = models.CharField(max_length=80, blank=True)
    fpa_ra = models.CharField(max_length=80, blank=True)
    fpa_rotangle = models.FloatField(null=True, blank=True)
    fpa_telescope = models.CharField(max_length=80, blank=True)
    fpa_teltemp_extra = models.FloatField(null=True, blank=True)
    fpa_teltemp_m1cell = models.FloatField(null=True, blank=True)
    fpa_teltemp_m1 = models.FloatField(null=True, blank=True)
    fpa_teltemp_m2 = models.FloatField(null=True, blank=True)
    fpa_teltemp_spider = models.FloatField(null=True, blank=True)
    fpa_teltemp_truss = models.FloatField(null=True, blank=True)
    fpa_temp = models.FloatField(null=True, blank=True)
    fsatur = models.FloatField(null=True, blank=True)
    fwhm_maj = models.FloatField(null=True, blank=True)
    fwhm_min = models.FloatField(null=True, blank=True)
    fw_mj_lq = models.FloatField(null=True, blank=True)
    fw_mj_sg = models.FloatField(null=True, blank=True)
    fw_mj_uq = models.FloatField(null=True, blank=True)
    fw_mn_lq = models.FloatField(null=True, blank=True)
    fw_mn_sg = models.FloatField(null=True, blank=True)
    fw_mn_uq = models.FloatField(null=True, blank=True)
    imageid = models.IntegerField(null=True, blank=True)
    imnaxis1 = models.IntegerField(null=True, blank=True)
    imnaxis2 = models.IntegerField(null=True, blank=True)
    mjd_obs = models.FloatField(unique=True, null=True, blank=True)
    msky_max = models.FloatField(null=True, blank=True)
    msky_min = models.FloatField(null=True, blank=True)
    msky_mn = models.FloatField(null=True, blank=True)
    msky_nx = models.IntegerField(null=True, blank=True)
    msky_ny = models.IntegerField(null=True, blank=True)
    msky_sig = models.FloatField(null=True, blank=True)
    ndet_cr = models.IntegerField(null=True, blank=True)
    ndet_ext = models.IntegerField(null=True, blank=True)
    npsfstar = models.IntegerField(null=True, blank=True)
    nstars = models.IntegerField(null=True, blank=True)
    photcode = models.CharField(max_length=80, blank=True)
    ppsub_input = models.CharField(max_length=80, blank=True)
    ppsub_kernel = models.CharField(max_length=80, blank=True)
    ppsub_reference = models.CharField(max_length=80, blank=True)
    pscamera = models.CharField(max_length=80, blank=True)
    psformat = models.CharField(max_length=80, blank=True)
    sourceid = models.IntegerField(null=True, blank=True)
    zero_pt = models.FloatField(null=True, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_cmf_metadata'
        managed = False

class TcsCrossMatches(models.Model):
    """TcsCrossMatches.
    """

    transient_object_id = models.IntegerField(null=True, blank=True)
    catalogue_object_id = models.CharField(max_length=30, blank=True)
    catalogue_table_id = models.ForeignKey(TcsCatalogueTables, to_field='id', db_column='catalogue_table_id', on_delete=models.CASCADE)
    search_parameters_id = models.IntegerField(null=True, blank=True)
    separation = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    z = models.FloatField(null=True, blank=True)
    scale = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    distance_modulus = models.FloatField(null=True, blank=True)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_cross_matches'
        managed = False

# 2013-06-05 KWS Swapped the order of the columns so that Django-Tables
#                can display the columns in the required order.
# 2013-10-25 KWS Moved observation status so that we can see it in the
#                quickview pages (for eliminating movers)
class TcsTransientObjects(models.Model):
    """TcsTransientObjects.
    """

    id = models.BigIntegerField(primary_key=True)
    followup_id = models.IntegerField(null=True, blank=True)
    followup_flag_date = models.DateField()
    ra_psf = models.FloatField()
    dec_psf = models.FloatField()
    object_classification = models.IntegerField(null=True, blank=True, db_column='object_classification')
    sherlockClassification = models.CharField(max_length=120, db_column='sherlockClassification')
    observation_status = models.CharField(max_length=40, blank=True)
    survey_field = models.CharField(max_length=10, blank=True)
    local_designation = models.CharField(max_length=40, blank=True)
    ps1_designation = models.CharField(max_length=40, blank=True)
    detection_list_id = models.ForeignKey(TcsDetectionLists, null=True, to_field='id', db_column='detection_list_id', on_delete=models.CASCADE)

    ipp_idet = models.IntegerField(null=True, blank=True)
    x_psf = models.FloatField(null=True, blank=True)
    y_psf = models.FloatField(null=True, blank=True)
    x_psf_sig = models.FloatField(null=True, blank=True)
    y_psf_sig = models.FloatField(null=True, blank=True)
    posangle = models.FloatField(null=True, blank=True)
    pltscale = models.FloatField(null=True, blank=True)
    psf_inst_mag = models.FloatField(null=True, blank=True)
    psf_inst_mag_sig = models.FloatField(null=True, blank=True)
    ap_mag = models.FloatField(null=True, blank=True)
    ap_mag_radius = models.FloatField(null=True, blank=True)
    peak_flux_as_mag = models.FloatField(null=True, blank=True)
    cal_psf_mag = models.FloatField(null=True, blank=True)
    cal_psf_mag_sig = models.FloatField(null=True, blank=True)
    sky = models.FloatField(null=True, blank=True)
    sky_sigma = models.FloatField(null=True, blank=True)
    psf_chisq = models.FloatField(null=True, blank=True)
    cr_nsigma = models.FloatField(null=True, blank=True)
    ext_nsigma = models.FloatField(null=True, blank=True)
    psf_major = models.FloatField(null=True, blank=True)
    psf_minor = models.FloatField(null=True, blank=True)
    psf_theta = models.FloatField(null=True, blank=True)
    psf_qf = models.FloatField(null=True, blank=True)
    psf_ndof = models.IntegerField(null=True, blank=True)
    psf_npix = models.IntegerField(null=True, blank=True)
    moments_xx = models.FloatField(null=True, blank=True)
    moments_xy = models.FloatField(null=True, blank=True)
    moments_yy = models.FloatField(null=True, blank=True)
    flags = models.IntegerField(null=True, blank=True)
    n_frames = models.IntegerField(null=True, blank=True)
    padding = models.IntegerField(null=True, blank=True)
    local_comments = models.CharField(max_length=255, blank=True)
    htm20id = models.IntegerField(null=True, db_column='htm20ID', blank=True) # Field name made lowercase.
    htm16id = models.IntegerField(null=True, db_column='htm16ID', blank=True) # Field name made lowercase.
    cx = models.FloatField(null=True, blank=True)
    cy = models.FloatField(null=True, blank=True)
    cz = models.FloatField(null=True, blank=True)
    tcs_cmf_metadata_id = models.ForeignKey(TcsCmfMetadata, to_field='id', db_column='tcs_cmf_metadata_id', on_delete=models.CASCADE)
#   This Foreign key reference to the classification flags table will need to be removed if the object
#   is to be a member of more than one classification.
    tcs_images_id = models.ForeignKey(TcsImages, to_field='id', db_column='tcs_images_id', on_delete=models.CASCADE)
    date_inserted = models.DateTimeField()
    date_modified = models.DateTimeField(null=True, blank=True)
#    object_classification = models.ForeignKey(TcsClassificationFlags, to_field='flag_id', db_column='object_classification', on_delete=models.CASCADE)
    followup_priority = models.IntegerField(null=True, blank=True)
    external_reference_id = models.CharField(max_length=40, blank=True)
    postage_stamp_request_id = models.ForeignKey(TcsPostageStampRequests, null=True, to_field='id', db_column='postage_stamp_request_id', on_delete=models.CASCADE)
    image_group_id = models.ForeignKey(TcsImageGroups, null=True, to_field='id', db_column='image_group_id', on_delete=models.CASCADE)


    # 2010-02-25 KWS Eight new columns added
    followup_counter = models.IntegerField(null=True, blank=True)
    other_designation = models.CharField(max_length=40, blank=True)
    rb_cat = models.FloatField(null=True, blank=True, db_column='classification_confidence')
    rb_pix = models.FloatField(null=True, blank=True, db_column='confidence_factor')
    quality_threshold_pass = models.BooleanField(null=True, blank=True)

    # 2010-06-11 KWS New columns added for diff stats, local magnitude calculations and zoo requests
    locally_calculated_mag = models.FloatField(null=True, blank=True)
    zoo_request_id = models.ForeignKey(TcsZooRequests, null=True, to_field='id', db_column='zoo_request_id', on_delete=models.CASCADE)
    psf_inst_flux = models.FloatField(null=True, blank=True)
    psf_inst_flux_sig = models.FloatField(null=True, blank=True)
    diff_npos = models.IntegerField(null=True, blank=True)
    diff_fratio = models.FloatField(null=True, blank=True)
    diff_nratio_bad = models.FloatField(null=True, blank=True)
    diff_nratio_mask = models.FloatField(null=True, blank=True)
    diff_nratio_all = models.FloatField(null=True, blank=True)

    # 2011-02-24 KWS New column added for Observation Status and Current Trend
    current_trend = models.CharField(max_length=40, blank=True)

    # 2013-12-05 KWS Added processing_status for processing flag defs
    processing_flags = models.IntegerField(null=True, blank=True)

    # 2021-06-09 KWS Added the 'xt' flag (suspected crosstalk)
    xt = models.IntegerField(null=True, blank=True)


    class Meta:
        """Meta.
        """

        db_table = 'tcs_transient_objects'
        managed = False

    @property
    def flags_bin(self):
       """flags_bin.
       """
       a = bin(int(str(self.flags)),32)
       return a

    @property
    def instrument_mag(self):
       """instrument_mag.
       """
       zero_pt = self.tcs_cmf_metadata_id.zero_pt
       exptime = self.tcs_cmf_metadata_id.exptime
       if zero_pt == None or self.psf_inst_mag == None or exptime == None:
           imag = None
       else:
           imag = self.psf_inst_mag + 2.5 * log10(exptime) + zero_pt
       return imag

    @property
    def aperture_mag(self):
       """aperture_mag.
       """
       zero_pt = self.tcs_cmf_metadata_id.zero_pt
       exptime = self.tcs_cmf_metadata_id.exptime
       if zero_pt == None or self.ap_mag == None or exptime == None:
           amag = None
       else:
           amag = self.ap_mag + 2.5 * log10(exptime) + zero_pt
       return amag

    @property
    def calibrated_mag(self):
       """calibrated_mag.
       """
       zero_pt = self.tcs_cmf_metadata_id.zero_pt
       exptime = self.tcs_cmf_metadata_id.exptime
       if zero_pt == None or self.cal_psf_mag == None or exptime == None:
           cmag = None
       else:
           cmag = self.cal_psf_mag + 2.5 * log10(exptime) + zero_pt
       return cmag

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.ra_psf)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.dec_psf)
        return dec_in_sex

    @property
    def ra_in_hours(self):
        """ra_in_hours.
        """
        ra_hours = ra_in_decimal_hours(self.ra_psf)
        return ra_hours

    # 2013-02-05 KWS Add decoded flag bits and break the foreign key relation for object_classification
    @property
    def decode_flag_bits(self):
        """decode_flag_bits.
        """
        object_definition = getFlagDefs(self.object_classification, FLAGS, delimiter = ' ')
        return object_definition

    # 2013-12-05 KWS Add decoded flag bits for processing_status
    @property
    def decode_processing_flags_bits(self):
        """decode_processing_flags_bits.
        """
        pf = getFlagDefs(self.processing_flags, PROCESSING_FLAGS, delimiter = ' ')
        sys.stderr.write('\nFLAG VALUE:%d\n' % self.processing_flags)
        sys.stderr.write('\nFLAG DEFS:%s\n' % pf)
        return pf


class TcsTransientReobservations(models.Model):
    """TcsTransientReobservations.
    """

    ipp_idet = models.IntegerField(null=True, blank=True)
    x_psf = models.FloatField(null=True, blank=True)
    y_psf = models.FloatField(null=True, blank=True)
    x_psf_sig = models.FloatField(null=True, blank=True)
    y_psf_sig = models.FloatField(null=True, blank=True)
    ra_psf = models.FloatField()
    dec_psf = models.FloatField()
    posangle = models.FloatField(null=True, blank=True)
    pltscale = models.FloatField(null=True, blank=True)
    psf_inst_mag = models.FloatField(null=True, blank=True)
    psf_inst_mag_sig = models.FloatField(null=True, blank=True)
    ap_mag = models.FloatField(null=True, blank=True)
    ap_mag_radius = models.FloatField(null=True, blank=True)
    peak_flux_as_mag = models.FloatField(null=True, blank=True)
    cal_psf_mag = models.FloatField(null=True, blank=True)
    cal_psf_mag_sig = models.FloatField(null=True, blank=True)
    sky = models.FloatField(null=True, blank=True)
    sky_sigma = models.FloatField(null=True, blank=True)
    psf_chisq = models.FloatField(null=True, blank=True)
    cr_nsigma = models.FloatField(null=True, blank=True)
    ext_nsigma = models.FloatField(null=True, blank=True)
    psf_major = models.FloatField(null=True, blank=True)
    psf_minor = models.FloatField(null=True, blank=True)
    psf_theta = models.FloatField(null=True, blank=True)
    psf_qf = models.FloatField(null=True, blank=True)
    psf_ndof = models.IntegerField(null=True, blank=True)
    psf_npix = models.IntegerField(null=True, blank=True)
    moments_xx = models.FloatField(null=True, blank=True)
    moments_xy = models.FloatField(null=True, blank=True)
    moments_yy = models.FloatField(null=True, blank=True)
    flags = models.IntegerField(null=True, blank=True)
    n_frames = models.IntegerField(null=True, blank=True)
    padding = models.IntegerField(null=True, blank=True)
    htm20id = models.IntegerField(db_column='htm20ID') # Field name made lowercase.
    htm16id = models.IntegerField(db_column='htm16ID') # Field name made lowercase.
    cx = models.FloatField()
    cy = models.FloatField()
    cz = models.FloatField()
    id = models.BigIntegerField(primary_key=True)
    tcs_cmf_metadata_id = models.ForeignKey(TcsCmfMetadata, to_field='id', db_column='tcs_cmf_metadata_id', on_delete=models.CASCADE)
    tcs_images_id = models.ForeignKey(TcsImages, to_field='id', db_column='tcs_images_id', on_delete=models.CASCADE)
    transient_object_id = models.BigIntegerField()
    date_inserted = models.DateTimeField()
    date_modified = models.DateTimeField(null=True, blank=True)
    local_comments = models.CharField(max_length=255, blank=True)
    postage_stamp_request_id = models.ForeignKey(TcsPostageStampRequests, null=True, to_field='id', db_column='postage_stamp_request_id', on_delete=models.CASCADE)
    image_group_id = models.ForeignKey(TcsImageGroups, null=True, to_field='id', db_column='image_group_id', on_delete=models.CASCADE)

    # 2010-02-25 KWS New column added
    quality_threshold_pass = models.BooleanField(null=True, blank=True)

    # 2010-06-11 KWS New columns added for diff stats and local magnitude calculations
    locally_calculated_mag = models.FloatField(null=True, blank=True)
    psf_inst_flux = models.FloatField(null=True, blank=True)
    psf_inst_flux_sig = models.FloatField(null=True, blank=True)
    diff_npos = models.IntegerField(null=True, blank=True)
    diff_fratio = models.FloatField(null=True, blank=True)
    diff_nratio_bad = models.FloatField(null=True, blank=True)
    diff_nratio_mask = models.FloatField(null=True, blank=True)
    diff_nratio_all = models.FloatField(null=True, blank=True)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_transient_reobservations'
        managed = False

    @property
    def flags_bin(self):
       """flags_bin.
       """
       a = bin(int(str(self.flags)),32)
       return a

    @property
    def instrument_mag(self):
       """instrument_mag.
       """
       zero_pt = self.tcs_cmf_metadata_id.zero_pt
       exptime = self.tcs_cmf_metadata_id.exptime
       if zero_pt == None or self.psf_inst_mag == None or exptime == None:
           imag = None
       else:
           imag = self.psf_inst_mag + 2.5 * log10(exptime) + zero_pt
       return imag

    @property
    def aperture_mag(self):
       """aperture_mag.
       """
       zero_pt = self.tcs_cmf_metadata_id.zero_pt
       exptime = self.tcs_cmf_metadata_id.exptime
       if zero_pt == None or self.ap_mag == None or exptime == None:
           amag = None
       else:
           amag = self.ap_mag + 2.5 * log10(exptime) + zero_pt
       return amag

    @property
    def calibrated_mag(self):
       """calibrated_mag.
       """
       zero_pt = self.tcs_cmf_metadata_id.zero_pt
       exptime = self.tcs_cmf_metadata_id.exptime
       if zero_pt == None or self.cal_psf_mag == None or exptime == None:
           cmag = None
       else:
           cmag = self.cal_psf_mag + 2.5 * log10(exptime) + zero_pt
       return cmag

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.ra_psf)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.dec_psf)
        return dec_in_sex

    @property
    def ra_in_hours(self):
        """ra_in_hours.
        """
        ra_hours = ra_in_decimal_hours(self.ra_psf)
        return ra_hours

# 2011-10-13 KWS Added new model for tcs_ipp_to_cfa_lookup

class TcsIppToCfaLookup(models.Model):
    """TcsIppToCfaLookup.
    """

    transient_object_id = models.BigIntegerField(db_column='transient_object_id', primary_key=True)
    eventID = models.BigIntegerField(null=True, blank=True)
    cfa_designation = models.CharField(max_length=45, db_column='cfa_designation')
    separation = models.FloatField(null=True, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_ipp_to_cfa_lookup'
        managed = False


# 2013-10-21 KWS Added new model for tcs_cross_matches_external
class TcsCrossMatchesExternal(models.Model):
    """TcsCrossMatchesExternal.
    """

    id = models.IntegerField(primary_key=True)
    transient_object_id = models.ForeignKey(TcsTransientObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    external_designation = models.CharField(max_length=180)
    type = models.CharField(max_length=120, blank=True)
    host_galaxy = models.CharField(max_length=180, blank=True)
    mag = models.FloatField(null=True, blank=True)
    discoverer = models.CharField(max_length=900, blank=True)
    matched_list = models.CharField(max_length=300)
    other_info = models.CharField(max_length=900, blank=True)
    separation = models.FloatField(null=True, blank=True)
    comments = models.CharField(max_length=900, blank=True)
    url = models.CharField(max_length=900, blank=True)
    host_z = models.FloatField(blank=True, null=True)
    object_z = models.FloatField(blank=True, null=True)
    disc_date = models.DateTimeField(blank=True, null=True)
    disc_filter = models.CharField(max_length=150, blank=True)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_cross_matches_external'
        managed = False

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


class TcsObjectGroups(models.Model):
    """TcsObjectGroups.
    """

    #id = models.BigIntegerField(primary_key=True)  # This can't be used as an auto increment by Django!
    id = models.AutoField(primary_key=True)
    transient_object_id = models.ForeignKey(TcsTransientObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    object_group_id = models.ForeignKey(TcsObjectGroupDefinitions, to_field='id', db_column='object_group_id', on_delete=models.CASCADE)
    class Meta:
        """Meta.
        """

        db_table = 'tcs_object_groups'
        managed = False

# 2015-11-17 KWS Added tcs_processing_status. We'll use the contents of this table to
#                stop users making updates when the database is locked.
class TcsProcessingStatus(models.Model):
    """TcsProcessingStatus.
    """

    id = models.BigIntegerField(primary_key=True)
    status = models.IntegerField()
    started = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_processing_status'

# 2017-05-09 KWS Added TcsObjectComments table. Comments will be inserted here in future.
class TcsObjectComments(models.Model):
    """TcsObjectComments.
    """

    id = models.BigIntegerField(db_column='id', primary_key=True)
    transient_object_id = models.ForeignKey(TcsTransientObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    date_inserted = models.DateTimeField(db_column='date_inserted', blank=False, null=False)
    comment = models.CharField(max_length=768, db_column='comment', blank=True, null=True)
    username = models.CharField(max_length=90, db_column='username', blank=True, null=True)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_object_comments'
        managed = False

# 2017-03-21 KWS Four new database tables for Sherlock and Gravitational Waves.
# 2017-06-20 KWS Dave has updated the definition of sherlock_classifications.
class SherlockClassifications(models.Model):
    """SherlockClassifications.
    """

    transient_object_id = models.OneToOneField(TcsTransientObjects, to_field='id', db_column='transient_object_id', primary_key=True, on_delete=models.CASCADE)
    classification = models.CharField(max_length=45, blank=True, null=True)
    annotation = models.TextField(blank=True, null=True)
    summary = models.CharField(max_length=50, blank=True, null=True)
    matchverified = models.IntegerField(db_column='matchVerified', blank=True, null=True)  # Field name made lowercase.
    developmentcomment = models.CharField(db_column='developmentComment', max_length=100, blank=True, null=True)  # Field name made lowercase.
    datelastmodified = models.DateTimeField(db_column='dateLastModified', blank=True, null=True)  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='dateCreated', blank=True, null=True)  # Field name made lowercase.
    updated = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'sherlock_classifications'


# 2017-06-20 KWS Dave has updated the definition of sherlock_crossmatches.
class SherlockCrossmatches(models.Model):
    """SherlockCrossmatches.
    """

    transient_object_id = models.ForeignKey(TcsTransientObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    catalogue_object_id = models.CharField(max_length=30, blank=True, null=True)
    catalogue_table_id = models.SmallIntegerField(blank=True, null=True)
    separationarcsec = models.FloatField(db_column='separationArcsec', blank=True, null=True)  # Field name made lowercase.
    northseparationarcsec = models.FloatField(db_column='northSeparationArcsec', blank=True, null=True)  # Field name made lowercase.
    eastseparationarcsec = models.FloatField(db_column='eastSeparationArcsec', blank=True, null=True)  # Field name made lowercase.
    id = models.BigIntegerField(primary_key=True)
    z = models.FloatField(blank=True, null=True)
    scale = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    distance_modulus = models.FloatField(blank=True, null=True)
    photoz = models.FloatField(db_column='photoZ', blank=True, null=True)  # Field name made lowercase.
    photozerr = models.FloatField(db_column='photoZErr', blank=True, null=True)  # Field name made lowercase.
    association_type = models.CharField(max_length=45, blank=True, null=True)
    datecreated = models.DateTimeField(db_column='dateCreated', blank=True, null=True)  # Field name made lowercase.
    physical_separation_kpc = models.FloatField(blank=True, null=True)
    catalogue_object_type = models.CharField(max_length=45, blank=True, null=True)
    catalogue_object_subtype = models.CharField(max_length=45, blank=True, null=True)
    association_rank = models.IntegerField(blank=True, null=True)
    catalogue_table_name = models.CharField(max_length=100, blank=True, null=True)
    catalogue_view_name = models.CharField(max_length=100, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    rankscore = models.FloatField(db_column='rankScore', blank=True, null=True)  # Field name made lowercase.
    search_name = models.CharField(max_length=100, blank=True, null=True)
    major_axis_arcsec = models.FloatField(blank=True, null=True)
    direct_distance = models.FloatField(blank=True, null=True)
    direct_distance_scale = models.FloatField(blank=True, null=True)
    direct_distance_modulus = models.FloatField(blank=True, null=True)
    radeg = models.FloatField(db_column='raDeg', blank=True, null=True)  # Field name made lowercase.
    decdeg = models.FloatField(db_column='decDeg', blank=True, null=True)  # Field name made lowercase.
    original_search_radius_arcsec = models.FloatField(blank=True, null=True)
    catalogue_view_id = models.IntegerField(blank=True, null=True)
    u = models.FloatField(db_column='U', blank=True, null=True)  # Field name made lowercase.
    uerr = models.FloatField(db_column='UErr', blank=True, null=True)  # Field name made lowercase.
    b = models.FloatField(db_column='B', blank=True, null=True)  # Field name made lowercase.
    berr = models.FloatField(db_column='BErr', blank=True, null=True)  # Field name made lowercase.
    v = models.FloatField(db_column='V', blank=True, null=True)  # Field name made lowercase.
    verr = models.FloatField(db_column='VErr', blank=True, null=True)  # Field name made lowercase.
    r = models.FloatField(db_column='R', blank=True, null=True)  # Field name made lowercase.
    rerr = models.FloatField(db_column='RErr', blank=True, null=True)  # Field name made lowercase.
    i = models.FloatField(db_column='I', blank=True, null=True)  # Field name made lowercase.
    ierr = models.FloatField(db_column='IErr', blank=True, null=True)  # Field name made lowercase.
    j = models.FloatField(db_column='J', blank=True, null=True)  # Field name made lowercase.
    jerr = models.FloatField(db_column='JErr', blank=True, null=True)  # Field name made lowercase.
    h = models.FloatField(db_column='H', blank=True, null=True)  # Field name made lowercase.
    herr = models.FloatField(db_column='HErr', blank=True, null=True)  # Field name made lowercase.
    k = models.FloatField(db_column='K', blank=True, null=True)  # Field name made lowercase.
    kerr = models.FloatField(db_column='KErr', blank=True, null=True)  # Field name made lowercase.
    field_u = models.FloatField(db_column='_u', blank=True, null=True)  # Field renamed because it started with '_'.
    field_uerr = models.FloatField(db_column='_uErr', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_g = models.FloatField(db_column='_g', blank=True, null=True)  # Field renamed because it started with '_'.
    field_gerr = models.FloatField(db_column='_gErr', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_r = models.FloatField(db_column='_r', blank=True, null=True)  # Field renamed because it started with '_'.
    field_rerr = models.FloatField(db_column='_rErr', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_i = models.FloatField(db_column='_i', blank=True, null=True)  # Field renamed because it started with '_'.
    field_ierr = models.FloatField(db_column='_iErr', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_z = models.FloatField(db_column='_z', blank=True, null=True)  # Field renamed because it started with '_'.
    field_zerr = models.FloatField(db_column='_zErr', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    field_y = models.FloatField(db_column='_y', blank=True, null=True)  # Field renamed because it started with '_'.
    field_yerr = models.FloatField(db_column='_yErr', blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    g = models.FloatField(db_column='G', blank=True, null=True)  # Field name made lowercase.
    gerr = models.FloatField(db_column='GErr', blank=True, null=True)  # Field name made lowercase.
    unkmag = models.FloatField(db_column='unkMag', blank=True, null=True)  # Field name made lowercase.
    unkmagerr = models.FloatField(db_column='unkMagErr', blank=True, null=True)  # Field name made lowercase.
    datelastmodified = models.DateTimeField(db_column='dateLastModified', blank=True, null=True)  # Field name made lowercase.
    updated = models.IntegerField(blank=True, null=True)
    classificationreliability = models.IntegerField(db_column='classificationReliability', blank=True, null=True)  # Field name made lowercase.
    transientabsmag = models.FloatField(db_column='transientAbsMag', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'sherlock_crossmatches'


class TcsGravityEvents(models.Model):
    """TcsGravityEvents.
    """

    gravity_event_id = models.CharField(primary_key=True, max_length=10)
    gracedb_id = models.CharField(max_length=10)
    mjd = models.FloatField(blank=True, null=True)
    datelastmodified = models.DateTimeField(db_column='dateLastModified', blank=True, null=True)  # Field name made lowercase.
    updated = models.IntegerField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_gravity_events'
        managed = False


class TcsGravityEventAnnotations(models.Model):
    """TcsGravityEventAnnotations.
    """

    primaryid = models.BigIntegerField(db_column='primaryId', primary_key=True)  # Field name made lowercase.
    transient_object_id = models.ForeignKey(TcsTransientObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    gravity_event_id = models.ForeignKey(TcsGravityEvents, to_field='gravity_event_id', db_column='gravity_event_id', on_delete=models.CASCADE)
    gracedb_id = models.CharField(max_length=10)
    enclosing_contour = models.IntegerField(blank=True, null=True)
    map_name = models.CharField(max_length=30, blank=True, null=True)
    datelastmodified = models.DateTimeField(db_column='dateLastModified', blank=True, null=True)  # Field name made lowercase.
    updated = models.IntegerField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_gravity_event_annotations'
        managed = False
        unique_together = (('transient_object_id', 'gracedb_id'),)


# 2019-08-09 KWS Added TcsLatestObjectStats
class TcsLatestObjectStats(models.Model):
    """TcsLatestObjectStats.
    """

    id = models.OneToOneField(TcsTransientObjects, on_delete=models.CASCADE, db_column='id', related_name='stats', primary_key=True)
    latest_mjd = models.FloatField(blank=True, null=True)
    latest_mag = models.FloatField(blank=True, null=True)
    latest_filter = models.CharField(max_length=80, blank=True)
    earliest_mjd = models.FloatField(blank=True, null=True)
    earliest_mag = models.FloatField(blank=True, null=True)
    earliest_filter = models.CharField(max_length=80, blank=True)
    ra_avg = models.FloatField(blank=True, null=True)
    dec_avg = models.FloatField(blank=True, null=True)
    catalogue = models.CharField(max_length=60, blank=True)
    catalogue_object_id = models.CharField(max_length=30, blank=True)
    separation = models.FloatField(blank=True, null=True)
    external_crossmatches = models.CharField(max_length=330, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_latest_object_stats'

    @property
    def ra_sex(self):
        """ra_sex.
        """
        ra_in_sex = ra_to_sex (self.ra_avg)
        return ra_in_sex

    @property
    def dec_sex(self):
        """dec_sex.
        """
        dec_in_sex = dec_to_sex (self.dec_avg)
        return dec_in_sex

    @property
    def earliest_mjd_date(self):
        """earliest_mjd_date.
        """
        dateFraction = getDateFractionMJD(self.earliest_mjd, delimiter = '-')
        return dateFraction

    @property
    def latest_mjd_date(self):
        """latest_mjd_date.
        """
        dateFraction = getDateFractionMJD(self.latest_mjd, delimiter = '-')
        return dateFraction

# 2019-12-10 KWS Added TcsZooniverseScores table. Comments will be inserted here in future.
class TcsZooniverseScores(models.Model):
    """TcsZooniverseScores.
    """

    id = models.BigIntegerField(db_column='id', primary_key=True)
    transient_object_id = models.ForeignKey(TcsTransientObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    score = models.FloatField(blank=True, null=True)
    user1 = models.CharField(max_length=384, db_column='user1', blank=True, null=True)
    user2 = models.CharField(max_length=384, db_column='user2', blank=True, null=True)
    user3 = models.CharField(max_length=384, db_column='user3', blank=True, null=True)
    date_inserted = models.DateTimeField(db_column='date_inserted', blank=False, null=False)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_zooniverse_scores'
        managed = False
