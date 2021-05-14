-- Function to calculate the lunation from the current date.
-- It ASSUMES the AVERAGE lunation period, so may be slightly
-- inaccurate.

-- This script can ONLY be run by ROOT

drop function if exists lunation;

delimiter //
create function lunation(input_date datetime)
returns bigint
deterministic
no sql
begin
--   declare first_lunation bigint default 1078;
   declare first_lunation bigint default 0;

   -- Picked up the date from Google.  May need to alter this. Also need to decide
   -- if lunations start from NEW moon or FULL moon.
   -- NEW MOON
   -- declare first_lunation_date datetime default '2010-02-14 02:52';
   -- FULL MOON - used by PS1 DRM
   declare first_lunation_date datetime default '2010-01-30 06:18';
   declare lunation_number bigint default 1077;
   declare lunation_period double default 2551442.8896;
   set lunation_number = truncate((unix_timestamp(input_date) - unix_timestamp(first_lunation_date))/lunation_period+first_lunation, 0);
   return lunation_number;
end
//
delimiter ;
