create or replace view atlas_v_detectionsddc_flat as
select
d.`id` db_det_id,
d.`atlas_metadata_id`,
d.`atlas_object_id`,
d.`det_id`,
d.`ra`,
d.`dec`,
d.`mag`,
d.`dmag`,
d.`x`,
d.`y`,
d.`major`,
d.`minor`,
d.`phi`,
d.`det`,
d.`chin`,
d.`pvr`,
d.`ptr`,
d.`pmv`,
d.`pkn`,
d.`pno`,
d.`pbn`,
d.`pcr`,
d.`pxt`,
d.`psc`,
d.`dup`,
d.`wpflx`,
d.`dflx`,
d.`date_modified`,
d.`image_group_id`,
d.`quality_threshold_pass`,
d.`deprecated`,
d.`realbogus_factor`,
d.`htm16ID`,
d.`date_inserted`,
m.`id` meta_id,
m.`filename`,
m.`obs`,
m.`obj`,
m.`filt`,
m.`mjd`,
m.`texp`,
m.`ra` ra_pointing,
m.`dec` dec_pointing,
m.`pa`,
m.`nx`,
m.`ny`,
m.`rad`,
m.`fwmaj`,
m.`fwmin`,
m.`psfpa`,
m.`scale`,
m.`long`,
m.`lat`,
m.`elev`,
m.`rarms`,
m.`decrms`,
m.`magzpt`,
m.`skymag`,
m.`cloud`,
m.`mag5sig`,
m.`az`,
m.`alt`,
m.`lambda`,
m.`beta`,
m.`sunelong`,
m.`input`,
m.`reference`,
m.`htm16ID` htm16ID_pointing
from atlas_detectionsddc d
join atlas_metadataddc m
on m.id = d.atlas_metadata_id
;