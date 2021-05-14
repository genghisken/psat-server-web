-- Function to calculate the lunation from the current date.
-- It ASSUMES the AVERAGE lunation period, so may be slightly
-- inaccurate.

-- This script can ONLY be run by ROOT

drop function if exists mjdlunation;

delimiter //
create function mjdlunation(mjd double)
returns bigint
deterministic
no sql
begin
   declare first_lunation bigint default 0;

   declare unixtime double;

   -- FULL MOON - used by PS1 DRM
   declare first_lunation_date datetime default '2010-01-30 06:18';

   declare lunation_number bigint default -999;
   declare lunation_period double default 2551442.8896;

   -- Calculate current MJD
   -- mjd = unixtime/86400.0+2440587.5-2400000.5

   set unixtime = (mjd + 2400000.5 - 2440587.5) * 86400.0;

   set lunation_number = truncate((unixtime - unix_timestamp(first_lunation_date))/lunation_period+first_lunation, 0);

   return lunation_number;
end
//
delimiter ;
