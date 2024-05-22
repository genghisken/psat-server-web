DROP TRIGGER after_update_tcs_vra_rank;

DELIMITER $$

CREATE TRIGGER after_update_tcs_vra_rank
AFTER UPDATE ON tcs_vra_rank
FOR EACH ROW
BEGIN
    UPDATE atlas_diff_objects
    SET realbogus_factor = NEW.`rank`
    WHERE id = NEW.transient_object_id;
END
$$

DELIMITER ;

DROP TRIGGER after_insert_tcs_vra_rank;
DELIMITER $$

CREATE TRIGGER after_insert_tcs_vra_rank
AFTER INSERT ON tcs_vra_rank
FOR EACH ROW
BEGIN
    UPDATE atlas_diff_objects
    SET realbogus_factor = NEW.`rank`
    WHERE id = NEW.transient_object_id;
END
$$

DELIMITER ;
