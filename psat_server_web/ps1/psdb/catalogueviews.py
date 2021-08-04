from django.db import models


# Special Sloan Custom model for crossmatches ...
# No Meta class associated with this class.

class SloanCrossMatch(models.Model):
    """SloanCrossMatch.
    """

    id = models.IntegerField(primary_key=True)
    catalogue_object_id = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=60)
    Objid = models.BigIntegerField() # Field name made lowercase.
    type = models.IntegerField(null=True, blank=True)
    gfilt = models.FloatField(null=True, blank=True)
    rfilt = models.FloatField(null=True, blank=True)
    ifilt = models.FloatField(null=True, blank=True)
    zfilt = models.FloatField(null=True, blank=True)
    separation = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    scale = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    distance_modulus = models.FloatField(null=True, blank=True)
    association_type = models.IntegerField(null=True, blank=True)


# ... and Custom query for FGSS

# 2012-03-05 KWS Modified query so that the only table matched in the crossmatches
#                table is tcs_cat_sdss_stars_galaxies.  This is because we can now
#                have Milliquas matches here.
def getSloanCrossmatchData(transientObjectId):
    """getSloanCrossmatchData.

    Args:
        transientObjectId:
    """
    queryset = SloanCrossMatch.objects.raw('''
           select c.id,
                  c.catalogue_object_id,
                  t.description,
                  cat.Objid,
                  cat.type,
                  cat.g gfilt, cat.r rfilt, cat.i ifilt, cat.z zfilt,
                  c.separation,
                  c.z,
                  c.scale,
                  c.distance,
                  c.distance_modulus,
                  c.association_type
             from tcs_cross_matches c,
                  psdb_web_v_cat_sdss_stars_galaxies cat,
                  tcs_catalogue_tables t
            where c.transient_object_id = %s
              and cast(c.catalogue_object_id as unsigned) = cat.Objid
              and c.catalogue_table_id = t.id
              and t.table_name = 'tcs_cat_sdss_stars_galaxies'
         order by c.association_type, c.separation
        ''', [transientObjectId])

    return queryset






class PsdbWebVCatSdssStarsGalaxies(models.Model):
    """PsdbWebVCatSdssStarsGalaxies.
    """

    objid = models.BigIntegerField(primary_key=True, db_column='Objid') # Field name made lowercase.
    ra = models.FloatField()
    dec_ = models.FloatField()
    mode = models.IntegerField(null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    specobjid = models.BigIntegerField(null=True, db_column='specObjID', blank=True) # Field name made lowercase.
    petromag_u = models.FloatField(null=True, db_column='petroMag_u', blank=True) # Field name made lowercase.
    petromag_g = models.FloatField(null=True, db_column='petroMag_g', blank=True) # Field name made lowercase.
    petromag_r = models.FloatField(null=True, db_column='petroMag_r', blank=True) # Field name made lowercase.
    petromag_i = models.FloatField(null=True, db_column='petroMag_i', blank=True) # Field name made lowercase.
    petromag_z = models.FloatField(null=True, db_column='petroMag_z', blank=True) # Field name made lowercase.
    extinction_u = models.FloatField(null=True, blank=True)
    extinction_g = models.FloatField(null=True, blank=True)
    extinction_r = models.FloatField(null=True, blank=True)
    extinction_i = models.FloatField(null=True, blank=True)
    extinction_z = models.FloatField(null=True, blank=True)
    petromagerr_u = models.FloatField(null=True, db_column='petroMagErr_u', blank=True) # Field name made lowercase.
    petromagerr_g = models.FloatField(null=True, db_column='petroMagErr_g', blank=True) # Field name made lowercase.
    petromagerr_r = models.FloatField(null=True, db_column='petroMagErr_r', blank=True) # Field name made lowercase.
    petromagerr_i = models.FloatField(null=True, db_column='petroMagErr_i', blank=True) # Field name made lowercase.
    petromagerr_z = models.FloatField(null=True, db_column='petroMagErr_z', blank=True) # Field name made lowercase.
    z_redshift = models.FloatField(null=True, blank=True)
    zerr = models.FloatField(null=True, db_column='zErr', blank=True) # Field name made lowercase.
    dmod = models.FloatField(null=True, blank=True)
    rest_ug = models.FloatField(null=True, blank=True)
    rest_gr = models.FloatField(null=True, blank=True)
    rest_ri = models.FloatField(null=True, blank=True)
    rest_iz = models.FloatField(null=True, blank=True)
    absmag_u = models.FloatField(null=True, db_column='absMag_u', blank=True) # Field name made lowercase.
    absmag_g = models.FloatField(null=True, db_column='absMag_g', blank=True) # Field name made lowercase.
    absmag_r = models.FloatField(null=True, db_column='absMag_r', blank=True) # Field name made lowercase.
    absmag_i = models.FloatField(null=True, db_column='absMag_i', blank=True) # Field name made lowercase.
    absmag_z = models.FloatField(null=True, db_column='absMag_z', blank=True) # Field name made lowercase.
    u = models.FloatField(null=True, blank=True)
    g = models.FloatField(null=True, blank=True)
    r = models.FloatField(null=True, blank=True)
    i = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    err_u = models.FloatField(null=True, db_column='Err_u', blank=True) # Field name made lowercase.
    err_g = models.FloatField(null=True, db_column='Err_g', blank=True) # Field name made lowercase.
    err_r = models.FloatField(null=True, db_column='Err_r', blank=True) # Field name made lowercase.
    err_i = models.FloatField(null=True, db_column='Err_i', blank=True) # Field name made lowercase.
    err_z = models.FloatField(null=True, db_column='Err_z', blank=True) # Field name made lowercase.
    psfmag_u = models.FloatField(null=True, db_column='psfMag_u', blank=True) # Field name made lowercase.
    psfmag_g = models.FloatField(null=True, db_column='psfMag_g', blank=True) # Field name made lowercase.
    psfmag_r = models.FloatField(null=True, db_column='psfMag_r', blank=True) # Field name made lowercase.
    psfmag_i = models.FloatField(null=True, db_column='psfMag_i', blank=True) # Field name made lowercase.
    psfmag_z = models.FloatField(null=True, db_column='psfMag_z', blank=True) # Field name made lowercase.
    psfmagerr_u = models.FloatField(null=True, db_column='psfMagErr_u', blank=True) # Field name made lowercase.
    psfmagerr_g = models.FloatField(null=True, db_column='psfMagErr_g', blank=True) # Field name made lowercase.
    psfmagerr_r = models.FloatField(null=True, db_column='psfMagErr_r', blank=True) # Field name made lowercase.
    psfmagerr_i = models.FloatField(null=True, db_column='psfMagErr_i', blank=True) # Field name made lowercase.
    psfmagerr_z = models.FloatField(null=True, db_column='psfMagErr_z', blank=True) # Field name made lowercase.
    htm20id = models.BigIntegerField(null=True, db_column='htm20ID', blank=True) # Field name made lowercase.
    htm16id = models.BigIntegerField(null=True, db_column='htm16ID', blank=True) # Field name made lowercase.
    cx = models.FloatField(null=True, blank=True)
    cy = models.FloatField(null=True, blank=True)
    cz = models.FloatField(null=True, blank=True)
    class Meta:
        """Meta.
        """

        db_table = 'psdb_web_v_cat_sdss_stars_galaxies'
