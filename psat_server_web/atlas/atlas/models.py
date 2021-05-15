# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.


from django.db import models

from gkutils.commonutils import FLAGS, PROCESSING_FLAGS, getFlagDefs, ra_to_sex, dec_to_sex, getDateFractionMJD


class TcsDetectionLists(models.Model):
    """TcsDetectionLists.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=80, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_detection_lists'


class TcsImageGroups(models.Model):
    """TcsImageGroups.
    """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    group_type = models.IntegerField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_image_groups'


class AtlasMetadata(models.Model):
    """AtlasMetadata.
    """

    id = models.BigIntegerField(primary_key=True)
    filename = models.CharField(max_length=255, blank=True)
    expname = models.CharField(max_length=255, blank=True)
    object = models.CharField(max_length=255, blank=True)
    mjd_obs = models.FloatField(blank=True, null=True)
    filter = models.CharField(max_length=10, blank=True)
    pa = models.FloatField(blank=True, null=True)
    exptime = models.FloatField(blank=True, null=True)
    nx = models.IntegerField(blank=True, null=True)
    ny = models.IntegerField(blank=True, null=True)
    rad = models.IntegerField(blank=True, null=True)
    scale = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    elev = models.FloatField(blank=True, null=True)
    ra = models.FloatField(blank=True, null=True)
    dec = models.FloatField(blank=True, null=True)
    rarms = models.FloatField(blank=True, null=True)
    decrms = models.FloatField(blank=True, null=True)
    zp = models.FloatField(blank=True, null=True)
    skymag = models.FloatField(blank=True, null=True)
    cloud = models.FloatField(blank=True, null=True)
    mag5sig = models.FloatField(blank=True, null=True)
    az = models.FloatField(blank=True, null=True)
    alt = models.FloatField(blank=True, null=True)
    lambda_field = models.FloatField(db_column='lambda', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    beta = models.FloatField(blank=True, null=True)
    sunelong = models.FloatField(blank=True, null=True)
    htm16id = models.BigIntegerField(db_column='htm16ID', blank=True, null=True)  # Field name made lowercase.
    input = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=255, blank=True)
    date_inserted = models.DateTimeField()

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_metadata'


# 2018-09-20 KWS Added 5 new columns, apfit, bckgnd, gain, psfphi, ddcver.
class AtlasMetadataddc(models.Model):
    """AtlasMetadataddc.
    """

    id = models.BigIntegerField(primary_key=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    obs = models.CharField(unique=True, max_length=60, blank=True, null=True)
    obj = models.CharField(max_length=60, blank=True, null=True)
    filt = models.CharField(max_length=10, blank=True, null=True)
    mjd = models.FloatField(blank=True, null=True)
    texp = models.FloatField(blank=True, null=True)
    ra = models.FloatField(blank=True, null=True)
    dec = models.FloatField(blank=True, null=True)
    pa = models.FloatField(blank=True, null=True)
    nx = models.SmallIntegerField(blank=True, null=True)
    ny = models.SmallIntegerField(blank=True, null=True)
    rad = models.IntegerField(blank=True, null=True)
    fwmaj = models.FloatField(blank=True, null=True)
    fwmin = models.FloatField(blank=True, null=True)
    psfpa = models.FloatField(blank=True, null=True)
    scale = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    elev = models.FloatField(blank=True, null=True)
    rarms = models.FloatField(blank=True, null=True)
    decrms = models.FloatField(blank=True, null=True)
    magzpt = models.FloatField(blank=True, null=True)
    skymag = models.FloatField(blank=True, null=True)
    cloud = models.FloatField(blank=True, null=True)
    mag5sig = models.FloatField(blank=True, null=True)
    az = models.FloatField(blank=True, null=True)
    alt = models.FloatField(blank=True, null=True)
    lambda_field = models.FloatField(db_column='lambda', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    beta = models.FloatField(blank=True, null=True)
    sunelong = models.FloatField(blank=True, null=True)
    apfit = models.FloatField(blank=True, null=True)
    bckgnd = models.IntegerField(blank=True, null=True)
    gain = models.FloatField(blank=True, null=True)
    psfphi = models.FloatField(blank=True, null=True)
    ddcver = models.CharField(max_length=30, blank=True, null=True)
    input = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    htm16id = models.BigIntegerField(db_column='htm16ID', blank=True, null=True)  # Field name made lowercase.
    date_inserted = models.DateTimeField()

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_metadataddc'
        unique_together = (('filename', 'mjd'),)


class TcsImages(models.Model):
    """TcsImages.
    """

    id = models.BigIntegerField(primary_key=True)
    target = models.CharField(max_length=255)
    ref = models.CharField(max_length=255, blank=True)
    diff = models.CharField(max_length=255, blank=True)
    mjd_obs = models.FloatField()

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_images'

    @property
    def whole_mjd(self):
        """whole_mjd.
        """
        m = int(self.mjd_obs)
        return m


class AtlasDiffObjects(models.Model):
    """AtlasDiffObjects.
    """

    id = models.BigIntegerField(primary_key=True)
    followup_id = models.IntegerField(blank=True, null=True)
    followup_flag_date = models.DateField(blank=True, null=True)
    #detection_id = models.IntegerField()
    # Note the quoted model name in the foreign key. This model has not yet been defined.
    detection_id = models.ForeignKey('AtlasDiffDetections', to_field='id', db_column='detection_id', on_delete=models.CASCADE)
    ra = models.FloatField()
    dec = models.FloatField()
    object_classification = models.IntegerField(blank=True, null=True)
    sherlockClassification = models.CharField(max_length=120, blank=True)
    observation_status = models.CharField(max_length=40, blank=True)
    htm16id = models.BigIntegerField(db_column='htm16ID')  # Field name made lowercase.
    jtindex = models.IntegerField(blank=True, null=True)
    images_id = models.ForeignKey(TcsImages, to_field='id', db_column='images_id', on_delete=models.CASCADE)
    date_inserted = models.DateTimeField()
    date_modified = models.DateTimeField(blank=True, null=True)
    processing_flags = models.IntegerField(blank=True, null=True)
    updated_by = models.CharField(max_length=40, blank=True)
    followup_priority = models.IntegerField(blank=True, null=True)
    external_reference_id = models.CharField(max_length=40, blank=True)
    detection_list_id = models.ForeignKey(TcsDetectionLists, null=True, to_field='id', db_column='detection_list_id', on_delete=models.CASCADE)
    survey_field = models.CharField(max_length=10, blank=True)
    followup_counter = models.IntegerField(blank=True, null=True)
    atlas_designation = models.CharField(max_length=40, blank=True)
    other_designation = models.CharField(max_length=40, blank=True)
    current_trend = models.CharField(max_length=40, blank=True)
    local_comments = models.CharField(max_length=765, blank=True)
    ndetections = models.IntegerField(blank=True, null=True)
    realbogus_factor = models.FloatField(blank=True, null=True)
    zooniverse_score = models.FloatField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_diff_objects'

    @property
    def decode_flag_bits(self):
        """decode_flag_bits.
        """
        object_definition = getFlagDefs(self.object_classification, FLAGS, delimiter = ' ')
        return object_definition

    @property
    def decode_processing_flags_bits(self):
        """decode_processing_flags_bits.
        """
        pf = getFlagDefs(self.processing_flags, PROCESSING_FLAGS, delimiter = ' ')
        return pf

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


class AtlasDiffDetections(models.Model):
    """AtlasDiffDetections.
    """

    id = models.BigIntegerField(primary_key=True)
    atlas_metadata_id = models.ForeignKey(AtlasMetadata, to_field='id', db_column='atlas_metadata_id', on_delete=models.CASCADE)
    atlas_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='atlas_object_id', on_delete=models.CASCADE)
    tphot_id = models.IntegerField()
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    peakval = models.FloatField(blank=True, null=True)
    skyval = models.FloatField(blank=True, null=True)
    peakfit = models.FloatField(blank=True, null=True)
    dpeak = models.FloatField(blank=True, null=True)
    skyfit = models.FloatField(blank=True, null=True)
    flux = models.FloatField(blank=True, null=True)
    dflux = models.FloatField(blank=True, null=True)
    major = models.FloatField(blank=True, null=True)
    minor = models.FloatField(blank=True, null=True)
    phi = models.FloatField(blank=True, null=True)
    err = models.FloatField(blank=True, null=True)
    chi_n = models.FloatField(db_column='chi_N', blank=True, null=True)  # Field name made lowercase.
    ra = models.FloatField()
    dec = models.FloatField()
    mag = models.FloatField(blank=True, null=True)
    dm = models.FloatField(blank=True, null=True)
    peak = models.FloatField(blank=True, null=True)
    sky = models.FloatField(blank=True, null=True)
    varkrn = models.FloatField(blank=True, null=True)
    pstar = models.FloatField(blank=True, null=True)
    pkast = models.FloatField(blank=True, null=True)
    preal = models.FloatField(blank=True, null=True)
    star = models.IntegerField(blank=True, null=True)
    dstar = models.IntegerField(blank=True, null=True)
    mstar = models.FloatField(blank=True, null=True)
    kast = models.IntegerField(blank=True, null=True)
    dkast = models.IntegerField(blank=True, null=True)
    htm16id = models.BigIntegerField(db_column='htm16ID')  # Field name made lowercase.
    jtindex = models.IntegerField(blank=True, null=True)
    date_inserted = models.DateTimeField()
    date_modified = models.DateTimeField(blank=True, null=True)
    image_group_id = models.ForeignKey(TcsImageGroups, to_field='id', db_column='image_group_id', on_delete=models.CASCADE)
    quality_threshold_pass = models.IntegerField(blank=True, null=True)
    deprecated = models.IntegerField(blank=True, null=True)
    realbogus_factor = models.FloatField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_diff_detections'


class AtlasDetectionsddc(models.Model):
    """AtlasDetectionsddc.
    """

    id = models.BigIntegerField(primary_key=True)
    atlas_metadata_id = models.ForeignKey(AtlasMetadataddc, to_field='id', db_column='atlas_metadata_id', on_delete=models.CASCADE)
    atlas_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='atlas_object_id', on_delete=models.CASCADE)
    det_id = models.IntegerField()
    ra = models.FloatField(blank=True, null=True)
    dec = models.FloatField(blank=True, null=True)
    mag = models.FloatField(blank=True, null=True)
    dmag = models.FloatField(blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    major = models.FloatField(blank=True, null=True)
    minor = models.FloatField(blank=True, null=True)
    phi = models.FloatField(blank=True, null=True)
    det = models.IntegerField(blank=True, null=True)
    chin = models.FloatField(blank=True, null=True)
    pvr = models.SmallIntegerField(blank=True, null=True)
    ptr = models.SmallIntegerField(blank=True, null=True)
    pmv = models.SmallIntegerField(blank=True, null=True)
    pkn = models.SmallIntegerField(blank=True, null=True)
    pno = models.SmallIntegerField(blank=True, null=True)
    pbn = models.SmallIntegerField(blank=True, null=True)
    pcr = models.SmallIntegerField(blank=True, null=True)
    pxt = models.SmallIntegerField(blank=True, null=True)
    psc = models.SmallIntegerField(blank=True, null=True)
    dup = models.IntegerField(blank=True, null=True)
    wpflx = models.FloatField(blank=True, null=True)
    dflx = models.FloatField(blank=True, null=True)
    date_modified = models.DateTimeField(blank=True, null=True)
    image_group_id = models.BigIntegerField(blank=True, null=True)
    quality_threshold_pass = models.IntegerField(blank=True, null=True)
    deprecated = models.IntegerField(blank=True, null=True)
    realbogus_factor = models.FloatField(blank=True, null=True)
    htm16id = models.BigIntegerField(db_column='htm16ID', blank=True, null=True)  # Field name made lowercase.
    date_inserted = models.DateTimeField()

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_detectionsddc'



# 2018-01-30 KWS Added major and minor
# 2018-09-21 KWS Added apfit
# 2018-09-25 KWS Added foreign key to AtlasMetadataddc so we can pull out
#                the correct exposure time and apfit values.
class AtlasForcedPhotometry(models.Model):
    """AtlasForcedPhotometry.
    """

    id = models.BigIntegerField(primary_key=True)
    atlas_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='atlas_object_id', on_delete=models.CASCADE)
    expname = models.ForeignKey(AtlasMetadataddc, to_field='obs', db_column='expname', on_delete=models.CASCADE)
    #expname = models.CharField(max_length=255, blank=True)
    mjd_obs = models.FloatField(blank=True, null=True)
    ra = models.FloatField(blank=True, null=True)
    dec = models.FloatField(blank=True, null=True)
    filter = models.CharField(max_length=10, blank=True)
    mag = models.FloatField(blank=True, null=True)
    dm = models.FloatField(blank=True, null=True)
    snr = models.FloatField(blank=True, null=True)
    zp = models.FloatField(blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    peakval = models.FloatField(blank=True, null=True)
    skyval = models.FloatField(blank=True, null=True)
    peakfit = models.FloatField(blank=True, null=True)
    dpeak = models.FloatField(blank=True, null=True)
    skyfit = models.FloatField(blank=True, null=True)
    flux = models.FloatField(blank=True, null=True)
    dflux = models.FloatField(blank=True, null=True)
    dflux = models.FloatField(blank=True, null=True)
    chin = models.FloatField(blank=True, null=True)
    major = models.FloatField(blank=True, null=True)
    minor = models.FloatField(blank=True, null=True)
    snrdet = models.FloatField(blank=True, null=True)
    snrlimit = models.FloatField(blank=True, null=True)
    apfit = models.FloatField(blank=True, null=True)
    date_inserted = models.DateTimeField()
    limiting_mag = models.BooleanField(null=True, blank=True)
    redo_photometry = models.BooleanField(null=True, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_forced_photometry'


class TcsCatalogueTables(models.Model):
    """TcsCatalogueTables.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    table_name = models.CharField(max_length=40)
    description = models.CharField(max_length=60)
    url = models.CharField(max_length=255, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_catalogue_tables'


class TcsClassificationFlags(models.Model):
    """TcsClassificationFlags.
    """

    flag_id = models.IntegerField(primary_key=True)
    flag_name = models.CharField(max_length=30)
    description = models.CharField(max_length=80, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_classification_flags'


class TcsClassificationHistory(models.Model):
    """TcsClassificationHistory.
    """

    id = models.BigIntegerField(primary_key=True)
    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    last_classification = models.IntegerField()
    reclassification_date = models.DateTimeField()
    comments = models.CharField(max_length=255, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_classification_history'


class TcsCrossMatches(models.Model):
    """TcsCrossMatches.
    """

    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    catalogue_object_id = models.CharField(max_length=30)
    catalogue_table_id = models.IntegerField()
    search_parameters_id = models.IntegerField()
    separation = models.FloatField(blank=True, null=True)
    id = models.BigIntegerField(primary_key=True)
    z = models.FloatField(blank=True, null=True)
    scale = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    distance_modulus = models.FloatField(blank=True, null=True)
    association_type = models.IntegerField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_cross_matches'


class TcsCrossMatchesExternal(models.Model):
    """TcsCrossMatchesExternal.
    """

    id = models.BigIntegerField(primary_key=True)
    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    external_designation = models.CharField(max_length=60)
    type = models.CharField(max_length=40, blank=True)
    host_galaxy = models.CharField(max_length=60, blank=True)
    mag = models.FloatField(blank=True, null=True)
    discoverer = models.CharField(max_length=300, blank=True)
    matched_list = models.CharField(max_length=100)
    other_info = models.CharField(max_length=300, blank=True)
    separation = models.FloatField(blank=True, null=True)
    comments = models.CharField(max_length=300, blank=True)
    url = models.CharField(max_length=300, blank=True)
    host_z = models.FloatField(blank=True, null=True)
    object_z = models.FloatField(blank=True, null=True)
    disc_date = models.DateTimeField(blank=True, null=True)
    disc_filter = models.CharField(max_length=150, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_cross_matches_external'


class TcsFollowupPhotometry(models.Model):
    """TcsFollowupPhotometry.
    """

    id = models.BigIntegerField(primary_key=True)
    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    telescope_instrument_id = models.IntegerField()
    mjd = models.FloatField()
    filter = models.CharField(max_length=20, blank=True)
    mag = models.FloatField(blank=True, null=True)
    magerr = models.FloatField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_followup_photometry'


class TcsFollowupTelescopeInstruments(models.Model):
    """TcsFollowupTelescopeInstruments.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    telescope_id = models.IntegerField()
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=60)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_followup_telescope_instruments'


class TcsFollowupTelescopes(models.Model):
    """TcsFollowupTelescopes.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=60)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_followup_telescopes'


class TcsForcedPhotometry(models.Model):
    """TcsForcedPhotometry.
    """

    id = models.BigIntegerField(primary_key=True)
    postage_stamp_request_id = models.BigIntegerField(blank=True, null=True)
    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    rownum = models.IntegerField(blank=True, null=True)
    skycell = models.CharField(max_length=10, blank=True)
    mjd_obs = models.FloatField(blank=True, null=True)
    exptime = models.FloatField(blank=True, null=True)
    filter = models.CharField(max_length=20, blank=True)
    fpa_id = models.CharField(max_length=20, blank=True)
    x_psf = models.FloatField(blank=True, null=True)
    y_psf = models.FloatField(blank=True, null=True)
    x_psf_sig = models.FloatField(blank=True, null=True)
    y_psf_sig = models.FloatField(blank=True, null=True)
    posangle = models.FloatField(blank=True, null=True)
    pltscale = models.FloatField(blank=True, null=True)
    psf_inst_mag = models.FloatField(blank=True, null=True)
    psf_inst_mag_sig = models.FloatField(blank=True, null=True)
    psf_inst_flux = models.FloatField(blank=True, null=True)
    psf_inst_flux_sig = models.FloatField(blank=True, null=True)
    ap_mag = models.FloatField(blank=True, null=True)
    ap_mag_radius = models.FloatField(blank=True, null=True)
    peak_flux_as_mag = models.FloatField(blank=True, null=True)
    cal_psf_mag = models.FloatField(blank=True, null=True)
    cal_psf_mag_sig = models.FloatField(blank=True, null=True)
    ra_psf = models.FloatField()
    dec_psf = models.FloatField()
    sky = models.FloatField(blank=True, null=True)
    sky_sigma = models.FloatField(blank=True, null=True)
    psf_chisq = models.FloatField(blank=True, null=True)
    cr_nsigma = models.FloatField(blank=True, null=True)
    ext_nsigma = models.FloatField(blank=True, null=True)
    psf_major = models.FloatField(blank=True, null=True)
    psf_minor = models.FloatField(blank=True, null=True)
    psf_theta = models.FloatField(blank=True, null=True)
    psf_qf = models.FloatField(blank=True, null=True)
    psf_ndof = models.IntegerField(blank=True, null=True)
    psf_npix = models.IntegerField(blank=True, null=True)
    moments_xx = models.FloatField(blank=True, null=True)
    moments_xy = models.FloatField(blank=True, null=True)
    moments_yy = models.FloatField(blank=True, null=True)
    diff_npos = models.IntegerField(blank=True, null=True)
    diff_fratio = models.FloatField(blank=True, null=True)
    diff_nratio_bad = models.FloatField(blank=True, null=True)
    diff_nratio_mask = models.FloatField(blank=True, null=True)
    diff_nratio_all = models.FloatField(blank=True, null=True)
    flags = models.IntegerField(blank=True, null=True)
    n_frames = models.IntegerField(blank=True, null=True)
    padding = models.IntegerField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_forced_photometry'


# 2015-11-23 KWS Experiment with OneToOneField for id, since this is both
#                a primary key and a foreign key.
class TcsLatestObjectStats(models.Model):
    """TcsLatestObjectStats.
    """

    #id = models.OneToOneField(AtlasDiffObjects, on_delete=models.CASCADE, db_column='id', related_name='stats', primary_key=True, blank=True, null=True)
    id = models.OneToOneField(AtlasDiffObjects, on_delete=models.CASCADE, db_column='id', related_name='stats', primary_key=True)
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
    discovery_target = models.CharField(max_length=80, blank=True)

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


class TcsObjectGroupDefinitions(models.Model):
    """TcsObjectGroupDefinitions.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=80, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_object_group_definitions'


class TcsObjectGroups(models.Model):
    """TcsObjectGroups.
    """

    id = models.BigIntegerField(primary_key=True)
    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    object_group_id = models.IntegerField()

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_object_groups'


class TcsParameterDefinitions(models.Model):
    """TcsParameterDefinitions.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=20)
    value = models.CharField(max_length=40)
    units = models.CharField(max_length=40)
    catalogue_table_id = models.IntegerField()
    search_parameters_id = models.IntegerField()

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_parameter_definitions'


class TcsPostageStampImages(models.Model):
    """TcsPostageStampImages.
    """

    id = models.BigIntegerField(primary_key=True)
    image_type = models.CharField(max_length=20)
    image_filename = models.CharField(max_length=255)
    pss_filename = models.CharField(max_length=255, blank=True)
    mjd_obs = models.FloatField(blank=True, null=True)
    image_group_id = models.ForeignKey(TcsImageGroups, to_field='id', db_column='image_group_id', on_delete=models.CASCADE)
    pss_error_code = models.IntegerField()
    filter = models.CharField(max_length=80, blank=True)
    mask_ratio = models.FloatField(blank=True, null=True)
    mask_ratio_at_core = models.FloatField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_postage_stamp_images'


    @property
    def filename(self):
        """filename.
        """
        mjdstring = int(float(self.image_filename.split('_')[1]))
        f = str(mjdstring) + '/' + self.image_filename
        return f

    @property
    def stamp_mjd(self):
        """stamp_mjd.
        """
        return self.mjd_obs

    @property
    def whole_mjd(self):
        """whole_mjd.
        """
        # The second field is always the target MJD
        fields = self.image_filename.split('_')
        m = int(float(fields[1]))
        return m

class TcsPostageStampRequests(models.Model):
    """TcsPostageStampRequests.
    """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    pss_id = models.BigIntegerField(blank=True, null=True)
    download_attempts = models.IntegerField()
    status = models.IntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField(blank=True, null=True)
    request_type = models.IntegerField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_postage_stamp_requests'


class TcsPostageStampStatusCodes(models.Model):
    """TcsPostageStampStatusCodes.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=80, blank=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_postage_stamp_status_codes'


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


class TcsSearchParameters(models.Model):
    """TcsSearchParameters.
    """

    id = models.IntegerField(primary_key=True)  # AutoField?
    parameter_set_name = models.CharField(max_length=20)
    comments = models.CharField(max_length=80, blank=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_search_parameters'


class TcsZooRequests(models.Model):
    """TcsZooRequests.
    """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    zoo_id = models.BigIntegerField(blank=True, null=True)
    download_attempts = models.IntegerField()
    status = models.IntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'tcs_zoo_requests'

# 2017-03-21 KWS Four new database tables for Sherlock and Gravitational Waves.
# 2017-06-20 KWS Dave has updated the definition of sherlock_classifications.
class SherlockClassifications(models.Model):
    """SherlockClassifications.
    """

    transient_object_id = models.OneToOneField(AtlasDiffObjects, to_field='id', db_column='transient_object_id', primary_key=True, on_delete=models.CASCADE)
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

    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
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


class TcsGravityEventAnnotations(models.Model):
    """TcsGravityEventAnnotations.
    """

    primaryid = models.BigIntegerField(db_column='primaryId', primary_key=True)  # Field name made lowercase.
    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
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
        unique_together = (('transient_object_id', 'gracedb_id'),)

# 2017-05-09 KWS Added TcsObjectComments table. Comments will be inserted here in future.
class TcsObjectComments(models.Model):
    """TcsObjectComments.
    """

    id = models.BigIntegerField(db_column='id', primary_key=True)
    transient_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='transient_object_id', on_delete=models.CASCADE)
    date_inserted = models.DateTimeField(db_column='date_inserted', blank=False, null=False)
    comment = models.CharField(max_length=768, db_column='comment', blank=True, null=True)
    username = models.CharField(max_length=90, db_column='username', blank=True, null=True)

    class Meta:
        """Meta.
        """

        db_table = 'tcs_object_comments'


# 2019-06-06 KWS Added AtlasStackedForcedPhotometry table.
class AtlasStackedForcedPhotometry(models.Model):
    """AtlasStackedForcedPhotometry.
    """

    id = models.BigIntegerField(primary_key=True)
    atlas_object_id = models.ForeignKey(AtlasDiffObjects, to_field='id', db_column='atlas_object_id', on_delete=models.CASCADE)
    mjd = models.FloatField(blank=True, null=True)
    m = models.FloatField(blank=True, null=True)
    dm = models.FloatField(blank=True, null=True)
    ujy = models.FloatField(blank=True, null=True)
    dujy = models.FloatField(blank=True, null=True)
    f = models.CharField(max_length=10, blank=True, null=True)
    err = models.FloatField(blank=True, null=True)
    chin = models.FloatField(blank=True, null=True)
    ra = models.FloatField(blank=True, null=True)
    dec = models.FloatField(blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    maj = models.FloatField(blank=True, null=True)
    min = models.FloatField(blank=True, null=True)
    phi = models.FloatField(blank=True, null=True)
    apfit = models.FloatField(blank=True, null=True)
    sky = models.FloatField(blank=True, null=True)
    zp = models.FloatField(blank=True, null=True)
    stack = models.CharField(max_length=60, blank=True, null=True)
    date_inserted = models.DateTimeField()
    redo_photometry = models.IntegerField(blank=True, null=True)

    class Meta:
        """Meta.
        """

        managed = False
        db_table = 'atlas_stacked_forced_photometry'
