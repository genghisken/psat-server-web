DELIMITER $$
CREATE TRIGGER `sherlock_classifications_AFTER_INSERT` AFTER INSERT ON `sherlock_classifications` FOR EACH ROW
BEGIN
    update `tcs_transient_objects` set `sherlockClassification` = new.classification
                        where `id`  = new.transient_object_id;
END;
$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `sherlock_classifications_BEFORE_INSERT` BEFORE INSERT ON `sherlock_classifications` FOR EACH ROW
BEGIN
    IF new.classification = "ORPHAN" THEN
        SET new.annotation = "The transient location is not matched against any known catalogued source", new.summary = "No catalogued match";
    END IF;
END;
$$
DELIMITER ;

