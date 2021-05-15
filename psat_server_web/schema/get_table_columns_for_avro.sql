select column_name, data_type, is_nullable from information_schema.columns where table_schema = @schema COLLATE utf8_general_ci and table_name = @tablename COLLATE utf8_general_ci ;
