-- --------------------- USER user ---------------------------

drop user 'USER'@'%';
drop user 'USER'@'localhost';
grant all on DATABASE.* to 'USER'@'%' identified by 'PASSWORD';
grant all on DATABASE.* to 'USER'@'localhost' identified by 'PASSWORD';

-- 2012-02-15 KWS Add temporary table privs to the user
grant create temporary tables on DATABASE.* to 'USER'@'%' identified by 'PASSWORD';
grant create temporary tables on DATABASE.* to 'USER'@'localhost' identified by 'PASSWORD';

-- 2011-05-10 KWS Add execute permissions as well for stored routines.
--                Note that users CANNOT create or drop routines.
--                Only root user can do this.  I'm not willing to
--                grant SUPER to any users!
grant execute on DATABASE.* to 'USER'@'%';
grant execute on DATABASE.* to 'USER'@'localhost';

-- 2012-12-04 KWS Keeping track of all the catalogues in panstarrs1
--                is massive overhead.  Why not just grant select on
--                all tables in panstarrs1...

grant select on panstarrs1.* to 'USER'@'%';
grant select on panstarrs1.* to 'USER'@'localhost';

-- Django test schema
grant all on DATABASE_django.* to 'USER'@'%';
grant all on DATABASE_django.* to 'USER'@'localhost';

-- GPC1 schema
grant select on gpc1.* to 'USER'@'%';
grant select on gpc1.* to 'USER'@'localhost';

