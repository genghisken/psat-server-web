# Form display options file

PROMOTION_CHOICES = (
    ('Confirmed', 'Promote Object to Confirmed List'),
    ('Good', 'Promote Object to Good List'),
    ('Attic', 'Promote Object to Attic List'),
    ('Eyeball', 'Move Object to Eyeball List'),
    ('Possible', 'Promote Object to Possible List'),
    ('Garbage', 'Consign to Garbage'),
    ('DoNothing', 'Undecided - Comment only'),
)

# This is a bit dumb.  We will need to revise how we do these lists.

# It's an EYEBALL object
EYEBALL_PROMOTION_CHOICES = (
    ('Good', 'Promote Object to Good List'),
    ('Attic', 'Promote Object to Attic List'),
    ('Possible', 'Promote Object to Possible List'),
    ('Garbage', 'Consign to Garbage'),
    ('DoNothing', 'Undecided - Comment only'),
)

# It's a GOOD object
GOOD_POST_PROMOTION_CHOICES = (
    ('Confirmed', 'Promote Object to Confirmed List'),
    ('Attic', 'Move Object to Attic List'),
    ('Possible', 'Move Object to Possible List'),
    ('Garbage', 'Consign to Garbage'),
    ('DoNothing', 'Add a Comment'),
)

# It's a POSSIBLE object
POSSIBLE_POST_PROMOTION_CHOICES = (
    ('Good', 'Promote Object to Good List'),
    ('Attic', 'Move Object to Attic List'),
    ('Garbage', 'Consign to Garbage'),
    ('DoNothing', 'Add a Comment'),
)

# It's an ATTIC object
ATTIC_POST_PROMOTION_CHOICES = (
    ('Good', 'Promote Object to Good List'),
    ('Possible', 'Move Object to Possible List'),
    ('Garbage', 'Consign to Garbage'),
    ('DoNothing', 'Add a Comment'),
)

# It's a ZOO object
ZOO_POST_PROMOTION_CHOICES = (
    ('Good', 'Promote Object to Good List'),
    ('Attic', 'Move Object to Attic List'),
    ('Possible', 'Move Object to Possible List'),
    ('Eyeball', 'Move Object to Eyeball List'),
    ('Garbage', 'Consign to Garbage'),
    ('DoNothing', 'Add a Comment'),
)

# It's a CONFIRMED object
CONFIRMED_POST_PROMOTION_CHOICES = (
    ('Good', 'Move Object to Good List'),
    ('Attic', 'Move Object to Attic List'),
    ('Possible', 'Move Object to Possible List'),
    ('Garbage', 'Consign to Garbage'),
    ('DoNothing', 'Add a Comment'),
)

# 2011-10-04 KWS Need to be able to comment on garbage or return to eyeball
# It's in the GARBAGE.  Maybe we want to comment or promote back to EYEBALL.
GARBAGE_CHOICES = (
    ('Eyeball', 'Move Object to Eyeball List'),
    ('DoNothing', 'Add a Comment'),
)


# All the possible options for the object's observation status
OBSERVATION_STATUS_CHOICES = (
    (None, None),
    ('in Queue', 'in Queue'),
    ('in Queue NTT', 'in Queue NTT'),
    ('in Queue UH88', 'in Queue UH88'),
    ('in Queue LT', 'in Queue LT'),
    ('in Queue SOAR', 'in Queue SOAR'),
    ('in Queue Gemini N', 'in Queue Gemini N'),
    ('in Queue Gemini S', 'in Queue Gemini S'),
    ('in Queue WHT', 'in Queue WHT'),
    ('in Queue INT', 'in Queue INT'),
    ('in Queue Magellen', 'in Queue Magellan'),
    ('in Queue MMT', 'in Queue MMT'),
    ('in Queue NOT', 'in Queue NOT'),
    ('in Queue VLT', 'in Queue VLT'),
    ('in Queue APO', 'in Queue APO'),
    ('Observed', 'Observed'),
    ('AGN', 'AGN'),
    ('QSO', 'QSO'),
    ('Galaxy', 'Galaxy'),
    ('TDE', 'TDE'),
    ('CV', 'CV'),
    ('LBV', 'LBV'),
    ('Varstar', 'Varstar'),
    ('M dwarf', 'M dwarf'),
    ('ILRT', 'ILRT'),
    ('Nova', 'Nova'),
    ('Afterglow', 'Afterglow'),
    ('SN', 'SN'), # It's a SN but we don't yet know what type
    ('SN I', 'SN I'),
    ('SN I-faint', 'SN I-faint'),
    ('SN I-rapid', 'SN I-rapid'),
    ('SN Ia', 'SN Ia'),
    ('SN Ia-91bg-like', 'SN Ia-91bg-like'),
    ('SN Ia-91T-like', 'SN Ia-91T-like'),
    ('SN Ia-pec', 'SN Ia-pec'),
    ('SN Ia-CSM', 'SN Ia-CSM'),
    ('SN Ia-Ca-rich', 'SN Ia-Ca-rich'),
    ('SN Ia-SC', 'SN Ia-SC'),
    ('SN Iax[02cx-like]', 'SN Iax[02cx-like]'),
    ('SN Ib', 'SN Ib'),
    ('SN Ib-Ca-rich', 'SN Ib-Ca-rich'),
    ('SN Ib-pec', 'SN Ib-pec'),
    ('SN Ib/c', 'SN Ib/c'),
    ('SN Ib/c-pec', 'SN Ib/c-pec'),
    ('SN Ibn', 'SN Ibn'),
    ('SN Ic', 'SN Ic'),
    ('SN Ic-BL', 'SN Ic-BL'),
    ('SN Ic-pec', 'SN Ic-pec'),
    ('SN II', 'SN II'),
    ('SN II-pec', 'SN II-pec'),
    ('SN IIb', 'SN IIb'),
    ('SN IIL', 'SN IIL'),
    ('SN IIn', 'SN IIn'),
    ('SN IIn-pec', 'SN IIn-pec'),
    ('SN IIn / AGN', 'SN IIn / AGN'),
    ('SN IIP', 'SN IIP'),
    ('SN II 87A-like', 'SN II 87A-like'),
    ('Kilonova', 'Kilonova'),
    ('SLSN', 'SLSN'),
    ('SLSN-I', 'SLSN-I'),
    ('SLSN-II', 'SLSN-II'),
    ('SLSN-R', 'SLSN-R'),
    ('Impostor-SN', 'Impostor-SN'),
    ('mover', 'mover'),
    ('other', 'other'),
)

#WHOLE_SURVEY_LIFETIME        = 1
#JUST_RECENT_90_DAYS          = 2
#JUST_DETECTION_LIMITS        = 3
#USER_DEFINED_LIMITS          = 4

# 2011-08-30 KWS Added choices for redrawing light curves
LIGHTCURVE_REPLOTTING_CHOICES = (
    ('0', 'Do nothing'),
    ('1', 'Whole Survey Lifetime'),
    ('2', 'Most Recent 90 Days'),
    ('3', 'Just Detection Limits'),
    ('4', 'User Defined Date Limits'),
)

choiceSelectors = {'T': '0', 'C': '1', 'G': '2', 'P': '3', 'E': '4', 'A': '5', 'U': '1000'}

def getChoiceSelectorTemplate(choice, checked = ''):
    templateParameters = {'template': None, 'attrs': None}
    try:
        CHOICE_SELECTOR = '''
            <div class="radio-ugpt-%s">
              <input class="%s" type="radio" id="{{record.id}}_promote_demote_%s" value="%s" name="{{record.id}}_promote_demote" %s />
              <label for="{{record.id}}_promote_demote_%s">%s</label>
            </div>
        ''' % (choice.lower(), choice, choiceSelectors[choice], choice, checked, choiceSelectors[choice], choice)
        attrs={"th":{"id":"select_all_%s" % (choice.lower()), "name":"select_all_%s" % (choice.lower()), "value":"all_%s" % (choice.lower())}}
    except KeyError as e:
        CHOICE_SELECTOR = None
        attrs = None

    templateParameters['template'] = CHOICE_SELECTOR
    templateParameters['attrs'] = attrs
    return templateParameters

FILTER_DEFINITIONS = [{'fieldName': 'xt', 'fieldType': 'boolean', 'validValues': [None, 0, 1, False, True]},
                      {'fieldName': 'rb_pix', 'fieldType': 'float', 'validValues' : [0,1], 'rangeSuffixes': ['lt','lte','gt','gte']},
                      {'fieldName': 'realbogus_factor', 'fieldType': 'float', 'validValues' : [0,1]},
                      {'fieldName': 'earliest_mag', 'fieldType': 'float', 'validValues' : [], 'rangeSuffixes': ['lt','lte','gt','gte']},
                      {'fieldName': 'latest_mag', 'fieldType': 'float', 'validValues' : [], 'rangeSuffixes': ['lt','lte','gt','gte']},
                      {'fieldName': 'earliest_mjd', 'fieldType': 'float', 'validValues' : [], 'rangeSuffixes': ['lt','lte','gt','gte']},
                      {'fieldName': 'latest_mjd', 'fieldType': 'float', 'validValues' : [], 'rangeSuffixes': ['lt','lte','gt','gte']},
                      {'fieldName': 'followup_flag_date', 'fieldType': 'date', 'validValues' : [], 'rangeSuffixes': ['lt','lte','gt','gte']},
    ]
