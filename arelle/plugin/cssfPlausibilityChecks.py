'''
Created on Jan 4, 2015

@author: Gregorio Mongelli (Acsone S. A.)
(c) Copyright 2015 Acsone S. A., All rights reserved.
'''

import os, sys, time, traceback

from arelle import ModelDocument, RenderingEvaluator
from arelle.ModelDocument import Type
from arelle.XbrlConst import assertionSet
from arelle.FileSource import openFileSource
from arelle.Locale import format_string

linkbaseReferences = {'aset-c_01.00.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/aset-c_01.00.xml',
                      'aset-c_02.00_c_04.00.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/aset-c_02.00_c_04.00.xml',
                      'aset-c_03.00.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/aset-c_03.00.xml',
                      'aset-c_04.00.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/aset-c_04.00.xml',
                      'aset-c_05.01.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/aset-c_05.01.xml',
                      'cssf-find-prec.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/cssf-find-prec.xml',
                      'vr_cssf001_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf001_m-err-en.xml',
                      'vr_cssf001_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf001_m-lab-en.xml',
                      'vr_cssf002_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf002_m-err-en.xml',
                      'vr_cssf002_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf002_m-lab-en.xml',
                      'vr_cssf003_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf003_m-err-en.xml',
                      'vr_cssf003_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf003_m-lab-en.xml',
                      'vr_cssf004_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf004_p-err-en.xml',
                      'vr_cssf004_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf004_p-lab-en.xml',
                      'vr_cssf005_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf005_p-err-en.xml',
                      'vr_cssf005_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf005_p-lab-en.xml',
                      'vr_cssf006_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf006_p-err-en.xml',
                      'vr_cssf006_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf006_p-lab-en.xml',
                      'vr_cssf007_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf007_p-err-en.xml',
                      'vr_cssf007_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf007_p-lab-en.xml',
                      'vr_cssf008_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf008_p-err-en.xml',
                      'vr_cssf008_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf008_p-lab-en.xml',
                      'vr_cssf009_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf009_p-err-en.xml',
                      'vr_cssf009_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf009_p-lab-en.xml',
                      'vr_cssf010_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf010_m-err-en.xml',
                      'vr_cssf010_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf010_m-lab-en.xml',
                      'vr_cssf011_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf011_m-err-en.xml',
                      'vr_cssf011_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf011_m-lab-en.xml',
                      'vr_cssf012_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf012_m-err-en.xml',
                      'vr_cssf012_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf012_m-lab-en.xml',
                      'vr_cssf013_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf013_m-err-en.xml',
                      'vr_cssf013_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf013_m-lab-en.xml',
                      'vr_cssf014_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf014_m-err-en.xml',
                      'vr_cssf014_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf014_m-lab-en.xml',
                      'vr_cssf015_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf015_m-err-en.xml',
                      'vr_cssf015_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf015_m-lab-en.xml',
                      'vr_cssf016_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf016_m-err-en.xml',
                      'vr_cssf016_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf016_m-lab-en.xml',
                      'vr_cssf017aa_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aa_m-err-en.xml',
                      'vr_cssf017aa_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aa_m-lab-en.xml',
                      'vr_cssf017ab_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ab_m-err-en.xml',
                      'vr_cssf017ab_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ab_m-lab-en.xml',
                      'vr_cssf017ac_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ac_m-err-en.xml',
                      'vr_cssf017ac_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ac_m-lab-en.xml',
                      'vr_cssf017ad_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ad_m-err-en.xml',
                      'vr_cssf017ad_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ad_m-lab-en.xml',
                      'vr_cssf017ae_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ae_m-err-en.xml',
                      'vr_cssf017ae_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ae_m-lab-en.xml',
                      'vr_cssf017af_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017af_m-err-en.xml',
                      'vr_cssf017af_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017af_m-lab-en.xml',
                      'vr_cssf017ag_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ag_m-err-en.xml',
                      'vr_cssf017ag_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ag_m-lab-en.xml',
                      'vr_cssf017ah_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ah_m-err-en.xml',
                      'vr_cssf017ah_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ah_m-lab-en.xml',
                      'vr_cssf017ai_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ai_m-err-en.xml',
                      'vr_cssf017ai_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ai_m-lab-en.xml',
                      'vr_cssf017aj_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aj_m-err-en.xml',
                      'vr_cssf017aj_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aj_m-lab-en.xml',
                      'vr_cssf017ak_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ak_m-err-en.xml',
                      'vr_cssf017ak_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ak_m-lab-en.xml',
                      'vr_cssf017al_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017al_m-err-en.xml',
                      'vr_cssf017al_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017al_m-lab-en.xml',
                      'vr_cssf017am_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017am_m-err-en.xml',
                      'vr_cssf017am_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017am_m-lab-en.xml',
                      'vr_cssf017an_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017an_m-err-en.xml',
                      'vr_cssf017an_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017an_m-lab-en.xml',
                      'vr_cssf017ao_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ao_m-err-en.xml',
                      'vr_cssf017ao_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ao_m-lab-en.xml',
                      'vr_cssf017ap_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ap_m-err-en.xml',
                      'vr_cssf017ap_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ap_m-lab-en.xml',
                      'vr_cssf017aq_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aq_m-err-en.xml',
                      'vr_cssf017aq_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aq_m-lab-en.xml',
                      'vr_cssf017ar_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ar_m-err-en.xml',
                      'vr_cssf017ar_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ar_m-lab-en.xml',
                      'vr_cssf017as_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017as_m-err-en.xml',
                      'vr_cssf017as_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017as_m-lab-en.xml',
                      'vr_cssf017at_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017at_m-err-en.xml',
                      'vr_cssf017at_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017at_m-lab-en.xml',
                      'vr_cssf017au_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017au_m-err-en.xml',
                      'vr_cssf017au_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017au_m-lab-en.xml',
                      'vr_cssf017av_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017av_m-err-en.xml',
                      'vr_cssf017av_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017av_m-lab-en.xml',
                      'vr_cssf017aw_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aw_m-err-en.xml',
                      'vr_cssf017aw_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017aw_m-lab-en.xml',
                      'vr_cssf017ax_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ax_m-err-en.xml',
                      'vr_cssf017ax_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ax_m-lab-en.xml',
                      'vr_cssf017ay_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ay_m-err-en.xml',
                      'vr_cssf017ay_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ay_m-lab-en.xml',
                      'vr_cssf017az_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017az_m-err-en.xml',
                      'vr_cssf017az_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017az_m-lab-en.xml',
                      'vr_cssf017ba_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ba_m-err-en.xml',
                      'vr_cssf017ba_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017ba_m-lab-en.xml',
                      'vr_cssf017bb_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bb_m-err-en.xml',
                      'vr_cssf017bb_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bb_m-lab-en.xml',
                      'vr_cssf017bc_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bc_m-err-en.xml',
                      'vr_cssf017bc_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bc_m-lab-en.xml',
                      'vr_cssf017bd_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bd_m-err-en.xml',
                      'vr_cssf017bd_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bd_m-lab-en.xml',
                      'vr_cssf017be_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017be_m-err-en.xml',
                      'vr_cssf017be_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017be_m-lab-en.xml',
                      'vr_cssf017bf_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bf_m-err-en.xml',
                      'vr_cssf017bf_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bf_m-lab-en.xml',
                      'vr_cssf017bg_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bg_m-err-en.xml',
                      'vr_cssf017bg_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bg_m-lab-en.xml',
                      'vr_cssf017bh_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bh_m-err-en.xml',
                      'vr_cssf017bh_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bh_m-lab-en.xml',
                      'vr_cssf017bi_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bi_m-err-en.xml',
                      'vr_cssf017bi_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bi_m-lab-en.xml',
                      'vr_cssf017bj_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bj_m-err-en.xml',
                      'vr_cssf017bj_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bj_m-lab-en.xml',
                      'vr_cssf017bk_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bk_m-err-en.xml',
                      'vr_cssf017bk_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bk_m-lab-en.xml',
                      'vr_cssf017bl_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bl_m-err-en.xml',
                      'vr_cssf017bl_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bl_m-lab-en.xml',
                      'vr_cssf017bm_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bm_m-err-en.xml',
                      'vr_cssf017bm_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bm_m-lab-en.xml',
                      'vr_cssf017bn_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bn_m-err-en.xml',
                      'vr_cssf017bn_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bn_m-lab-en.xml',
                      'vr_cssf017bo_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bo_m-err-en.xml',
                      'vr_cssf017bo_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bo_m-lab-en.xml',
                      'vr_cssf017bp_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bp_m-err-en.xml',
                      'vr_cssf017bp_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bp_m-lab-en.xml',
                      'vr_cssf017bq_m-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bq_m-err-en.xml',
                      'vr_cssf017bq_m-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf017bq_m-lab-en.xml',
                      'vr_cssf018a0_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a0_p-err-en.xml',
                      'vr_cssf018a0_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a0_p-lab-en.xml',
                      'vr_cssf018a1_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a1_p-err-en.xml',
                      'vr_cssf018a1_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a1_p-lab-en.xml',
                      'vr_cssf018a2_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a2_p-err-en.xml',
                      'vr_cssf018a2_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a2_p-lab-en.xml',
                      'vr_cssf018a3_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a3_p-err-en.xml',
                      'vr_cssf018a3_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a3_p-lab-en.xml',
                      'vr_cssf018a4_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a4_p-err-en.xml',
                      'vr_cssf018a4_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a4_p-lab-en.xml',
                      'vr_cssf018a5_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a5_p-err-en.xml',
                      'vr_cssf018a5_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a5_p-lab-en.xml',
                      'vr_cssf018a6_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a6_p-err-en.xml',
                      'vr_cssf018a6_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a6_p-lab-en.xml',
                      'vr_cssf018a7_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a7_p-err-en.xml',
                      'vr_cssf018a7_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a7_p-lab-en.xml',
                      'vr_cssf018a8_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a8_p-err-en.xml',
                      'vr_cssf018a8_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a8_p-lab-en.xml',
                      'vr_cssf018a9_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a9_p-err-en.xml',
                      'vr_cssf018a9_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018a9_p-lab-en.xml',
                      'vr_cssf018aa_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aa_p-err-en.xml',
                      'vr_cssf018aa_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aa_p-lab-en.xml',
                      'vr_cssf018ab_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ab_p-err-en.xml',
                      'vr_cssf018ab_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ab_p-lab-en.xml',
                      'vr_cssf018ac_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ac_p-err-en.xml',
                      'vr_cssf018ac_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ac_p-lab-en.xml',
                      'vr_cssf018ae_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ae_p-err-en.xml',
                      'vr_cssf018ae_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ae_p-lab-en.xml',
                      'vr_cssf018af_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018af_p-err-en.xml',
                      'vr_cssf018af_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018af_p-lab-en.xml',
                      'vr_cssf018ah_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ah_p-err-en.xml',
                      'vr_cssf018ah_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ah_p-lab-en.xml',
                      'vr_cssf018ai_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ai_p-err-en.xml',
                      'vr_cssf018ai_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ai_p-lab-en.xml',
                      'vr_cssf018aj_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aj_p-err-en.xml',
                      'vr_cssf018aj_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aj_p-lab-en.xml',
                      'vr_cssf018ak_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ak_p-err-en.xml',
                      'vr_cssf018ak_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ak_p-lab-en.xml',
                      'vr_cssf018al_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018al_p-err-en.xml',
                      'vr_cssf018al_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018al_p-lab-en.xml',
                      'vr_cssf018am_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018am_p-err-en.xml',
                      'vr_cssf018am_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018am_p-lab-en.xml',
                      'vr_cssf018an_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018an_p-err-en.xml',
                      'vr_cssf018an_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018an_p-lab-en.xml',
                      'vr_cssf018ao_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ao_p-err-en.xml',
                      'vr_cssf018ao_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ao_p-lab-en.xml',
                      'vr_cssf018ap_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ap_p-err-en.xml',
                      'vr_cssf018ap_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ap_p-lab-en.xml',
                      'vr_cssf018aq_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aq_p-err-en.xml',
                      'vr_cssf018aq_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aq_p-lab-en.xml',
                      'vr_cssf018ar_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ar_p-err-en.xml',
                      'vr_cssf018ar_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ar_p-lab-en.xml',
                      'vr_cssf018as_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018as_p-err-en.xml',
                      'vr_cssf018as_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018as_p-lab-en.xml',
                      'vr_cssf018at_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018at_p-err-en.xml',
                      'vr_cssf018at_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018at_p-lab-en.xml',
                      'vr_cssf018au_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018au_p-err-en.xml',
                      'vr_cssf018au_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018au_p-lab-en.xml',
                      'vr_cssf018av_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018av_p-err-en.xml',
                      'vr_cssf018av_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018av_p-lab-en.xml',
                      'vr_cssf018aw_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aw_p-err-en.xml',
                      'vr_cssf018aw_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018aw_p-lab-en.xml',
                      'vr_cssf018ax_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ax_p-err-en.xml',
                      'vr_cssf018ax_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ax_p-lab-en.xml',
                      'vr_cssf018ay_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ay_p-err-en.xml',
                      'vr_cssf018ay_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ay_p-lab-en.xml',
                      'vr_cssf018b1_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b1_p-err-en.xml',
                      'vr_cssf018b1_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b1_p-lab-en.xml',
                      'vr_cssf018b2_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b2_p-err-en.xml',
                      'vr_cssf018b2_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b2_p-lab-en.xml',
                      'vr_cssf018b3_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b3_p-err-en.xml',
                      'vr_cssf018b3_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b3_p-lab-en.xml',
                      'vr_cssf018b7_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b7_p-err-en.xml',
                      'vr_cssf018b7_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b7_p-lab-en.xml',
                      'vr_cssf018b8_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b8_p-err-en.xml',
                      'vr_cssf018b8_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b8_p-lab-en.xml',
                      'vr_cssf018b9_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b9_p-err-en.xml',
                      'vr_cssf018b9_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018b9_p-lab-en.xml',
                      'vr_cssf018bb_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bb_p-err-en.xml',
                      'vr_cssf018bb_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bb_p-lab-en.xml',
                      'vr_cssf018bc_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bc_p-err-en.xml',
                      'vr_cssf018bc_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bc_p-lab-en.xml',
                      'vr_cssf018bd_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bd_p-err-en.xml',
                      'vr_cssf018bd_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bd_p-lab-en.xml',
                      'vr_cssf018be_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018be_p-err-en.xml',
                      'vr_cssf018be_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018be_p-lab-en.xml',
                      'vr_cssf018bf_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bf_p-err-en.xml',
                      'vr_cssf018bf_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bf_p-lab-en.xml',
                      'vr_cssf018bh_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bh_p-err-en.xml',
                      'vr_cssf018bh_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bh_p-lab-en.xml',
                      'vr_cssf018bi_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bi_p-err-en.xml',
                      'vr_cssf018bi_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bi_p-lab-en.xml',
                      'vr_cssf018bj_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bj_p-err-en.xml',
                      'vr_cssf018bj_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bj_p-lab-en.xml',
                      'vr_cssf018bk_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bk_p-err-en.xml',
                      'vr_cssf018bk_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bk_p-lab-en.xml',
                      'vr_cssf018bl_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bl_p-err-en.xml',
                      'vr_cssf018bl_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bl_p-lab-en.xml',
                      'vr_cssf018bm_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bm_p-err-en.xml',
                      'vr_cssf018bm_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bm_p-lab-en.xml',
                      'vr_cssf018bn_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bn_p-err-en.xml',
                      'vr_cssf018bn_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bn_p-lab-en.xml',
                      'vr_cssf018bo_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bo_p-err-en.xml',
                      'vr_cssf018bo_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bo_p-lab-en.xml',
                      'vr_cssf018bp_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bp_p-err-en.xml',
                      'vr_cssf018bp_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bp_p-lab-en.xml',
                      'vr_cssf018bq_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bq_p-err-en.xml',
                      'vr_cssf018bq_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bq_p-lab-en.xml',
                      'vr_cssf018br_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018br_p-err-en.xml',
                      'vr_cssf018br_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018br_p-lab-en.xml',
                      'vr_cssf018bs_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bs_p-err-en.xml',
                      'vr_cssf018bs_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bs_p-lab-en.xml',
                      'vr_cssf018bt_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bt_p-err-en.xml',
                      'vr_cssf018bt_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bt_p-lab-en.xml',
                      'vr_cssf018bu_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bu_p-err-en.xml',
                      'vr_cssf018bu_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bu_p-lab-en.xml',
                      'vr_cssf018bv_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bv_p-err-en.xml',
                      'vr_cssf018bv_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bv_p-lab-en.xml',
                      'vr_cssf018bw_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bw_p-err-en.xml',
                      'vr_cssf018bw_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018bw_p-lab-en.xml',
                      'vr_cssf018by_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018by_p-err-en.xml',
                      'vr_cssf018by_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018by_p-lab-en.xml',
                      'vr_cssf018c3_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018c3_p-err-en.xml',
                      'vr_cssf018c3_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018c3_p-lab-en.xml',
                      'vr_cssf018c7_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018c7_p-err-en.xml',
                      'vr_cssf018c7_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018c7_p-lab-en.xml',
                      'vr_cssf018cb_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cb_p-err-en.xml',
                      'vr_cssf018cb_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cb_p-lab-en.xml',
                      'vr_cssf018cc_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cc_p-err-en.xml',
                      'vr_cssf018cc_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cc_p-lab-en.xml',
                      'vr_cssf018ce_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ce_p-err-en.xml',
                      'vr_cssf018ce_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ce_p-lab-en.xml',
                      'vr_cssf018cf_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cf_p-err-en.xml',
                      'vr_cssf018cf_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cf_p-lab-en.xml',
                      'vr_cssf018cg_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cg_p-err-en.xml',
                      'vr_cssf018cg_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cg_p-lab-en.xml',
                      'vr_cssf018ch_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ch_p-err-en.xml',
                      'vr_cssf018ch_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ch_p-lab-en.xml',
                      'vr_cssf018ci_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ci_p-err-en.xml',
                      'vr_cssf018ci_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ci_p-lab-en.xml',
                      'vr_cssf018cj_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cj_p-err-en.xml',
                      'vr_cssf018cj_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cj_p-lab-en.xml',
                      'vr_cssf018ck_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ck_p-err-en.xml',
                      'vr_cssf018ck_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ck_p-lab-en.xml',
                      'vr_cssf018cl_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cl_p-err-en.xml',
                      'vr_cssf018cl_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cl_p-lab-en.xml',
                      'vr_cssf018cm_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cm_p-err-en.xml',
                      'vr_cssf018cm_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cm_p-lab-en.xml',
                      'vr_cssf018cn_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cn_p-err-en.xml',
                      'vr_cssf018cn_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cn_p-lab-en.xml',
                      'vr_cssf018co_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018co_p-err-en.xml',
                      'vr_cssf018co_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018co_p-lab-en.xml',
                      'vr_cssf018cp_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cp_p-err-en.xml',
                      'vr_cssf018cp_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cp_p-lab-en.xml',
                      'vr_cssf018cq_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cq_p-err-en.xml',
                      'vr_cssf018cq_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cq_p-lab-en.xml',
                      'vr_cssf018cr_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cr_p-err-en.xml',
                      'vr_cssf018cr_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cr_p-lab-en.xml',
                      'vr_cssf018cs_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cs_p-err-en.xml',
                      'vr_cssf018cs_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cs_p-lab-en.xml',
                      'vr_cssf018ct_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ct_p-err-en.xml',
                      'vr_cssf018ct_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ct_p-lab-en.xml',
                      'vr_cssf018cu_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cu_p-err-en.xml',
                      'vr_cssf018cu_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cu_p-lab-en.xml',
                      'vr_cssf018cv_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cv_p-err-en.xml',
                      'vr_cssf018cv_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cv_p-lab-en.xml',
                      'vr_cssf018cw_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cw_p-err-en.xml',
                      'vr_cssf018cw_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cw_p-lab-en.xml',
                      'vr_cssf018cy_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cy_p-err-en.xml',
                      'vr_cssf018cy_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018cy_p-lab-en.xml',
                      'vr_cssf018d7_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018d7_p-err-en.xml',
                      'vr_cssf018d7_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018d7_p-lab-en.xml',
                      'vr_cssf018d8_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018d8_p-err-en.xml',
                      'vr_cssf018d8_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018d8_p-lab-en.xml',
                      'vr_cssf018da_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018da_p-err-en.xml',
                      'vr_cssf018da_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018da_p-lab-en.xml',
                      'vr_cssf018db_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018db_p-err-en.xml',
                      'vr_cssf018db_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018db_p-lab-en.xml',
                      'vr_cssf018dd_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dd_p-err-en.xml',
                      'vr_cssf018dd_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dd_p-lab-en.xml',
                      'vr_cssf018de_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018de_p-err-en.xml',
                      'vr_cssf018de_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018de_p-lab-en.xml',
                      'vr_cssf018dg_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dg_p-err-en.xml',
                      'vr_cssf018dg_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dg_p-lab-en.xml',
                      'vr_cssf018dh_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dh_p-err-en.xml',
                      'vr_cssf018dh_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dh_p-lab-en.xml',
                      'vr_cssf018di_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018di_p-err-en.xml',
                      'vr_cssf018di_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018di_p-lab-en.xml',
                      'vr_cssf018dj_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dj_p-err-en.xml',
                      'vr_cssf018dj_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dj_p-lab-en.xml',
                      'vr_cssf018dk_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dk_p-err-en.xml',
                      'vr_cssf018dk_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dk_p-lab-en.xml',
                      'vr_cssf018dl_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dl_p-err-en.xml',
                      'vr_cssf018dl_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dl_p-lab-en.xml',
                      'vr_cssf018dm_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dm_p-err-en.xml',
                      'vr_cssf018dm_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dm_p-lab-en.xml',
                      'vr_cssf018dn_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dn_p-err-en.xml',
                      'vr_cssf018dn_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dn_p-lab-en.xml',
                      'vr_cssf018do_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018do_p-err-en.xml',
                      'vr_cssf018do_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018do_p-lab-en.xml',
                      'vr_cssf018dp_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dp_p-err-en.xml',
                      'vr_cssf018dp_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dp_p-lab-en.xml',
                      'vr_cssf018dq_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dq_p-err-en.xml',
                      'vr_cssf018dq_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dq_p-lab-en.xml',
                      'vr_cssf018dr_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dr_p-err-en.xml',
                      'vr_cssf018dr_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dr_p-lab-en.xml',
                      'vr_cssf018ds_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ds_p-err-en.xml',
                      'vr_cssf018ds_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018ds_p-lab-en.xml',
                      'vr_cssf018dt_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dt_p-err-en.xml',
                      'vr_cssf018dt_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dt_p-lab-en.xml',
                      'vr_cssf018du_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018du_p-err-en.xml',
                      'vr_cssf018du_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018du_p-lab-en.xml',
                      'vr_cssf018dv_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dv_p-err-en.xml',
                      'vr_cssf018dv_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dv_p-lab-en.xml',
                      'vr_cssf018dw_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dw_p-err-en.xml',
                      'vr_cssf018dw_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dw_p-lab-en.xml',
                      'vr_cssf018dy_p-err-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dy_p-err-en.xml',
                      'vr_cssf018dy_p-lab-en.xml': 'http://www.cssf.lu/lu/fr/xbrl/crr/fws/corep/its-2013-02/2015-02-12/val/vr_cssf018dy_p-lab-en.xml',
}
sampleCssfID = 'cssfC_03.00'

def loadXML(filesource, selectTopView, reloadViews, modelXbrl, controller):
    startedAt = time.time()
    try:
        action = _("imported")
        profileStat = "import"
        if modelXbrl:
            ModelDocument.load(modelXbrl, filesource.url)
            if reloadViews:
                modelXbrl.relationshipSets.clear() # relationships have to be re-cached

    except ModelDocument.LoadingException:
        controller.showStatus(_("Loading terminated, unrecoverable error"), 20000)
        return
    except Exception as err:
        msg = _("Exception loading {0}: {1}, at {2}").format(
                 filesource.url,
                 err,
                 traceback.format_tb(sys.exc_info()[2]))
        # not sure if message box can be shown from background thread
        # tkinter.messagebox.showwarning(_("Exception loading"),msg, parent=self.parent)
        controller.addToLog(msg);
        controller.showStatus(_("Loading terminated, unrecoverable error"), 20000)
        return
    if modelXbrl and modelXbrl.modelDocument:
        statTime = time.time() - startedAt
        modelXbrl.profileStat(profileStat, statTime)
        controller.addToLog(format_string(controller.modelManager.locale, 
                                    _("%s %s in %.2f secs"), 
                                    (action, filesource.url, statTime)))
        if reloadViews:
            if modelXbrl.hasTableRendering:
                controller.showStatus(_("Initializing table rendering"))
                RenderingEvaluator.init(modelXbrl)
                controller.showStatus(_("CSSF files {0}, preparing views").format(action))
                controller.waitForUiThreadQueue() # force status update
                controller.uiThreadQueue.put((controller.showLoadedXbrl, [modelXbrl, True, selectTopView]))
    else:
        controller.addToLog(format_string(controller.modelManager.locale, 
                                    _("not successfully %s in %.2f secs"), 
                                    (action, time.time() - startedAt)))
        
def fileOpenURL(filename, modelXbrl, controller, selectTopView=False, reloadViews=False):
    if filename:
        filesource = None
        # check for archive files
        filesource = openFileSource(filename, controller,
                                    checkIfXmlIsEis=controller.modelManager.disclosureSystem and
                                    controller.modelManager.disclosureSystem.EFM)
        if filesource.isArchive and not filesource.selection:
            raise FileNotFoundError
            
    if filename:
        loadXML(filesource, selectTopView, reloadViews, modelXbrl, controller)

def loadAllCSSFFiles(controller):
    if controller.modelManager is None or controller.modelManager.modelXbrl is None:
        controller.addToLog(_("No DTS loaded."))
        return
    modelXbrl = controller.modelManager.modelXbrl
    currentAssertionSet = modelXbrl.relationshipSet(assertionSet)
    objectsFrom = currentAssertionSet.fromModelObjects()
    for obj in objectsFrom:
        if obj.id==sampleCssfID:
            # avoid reloading the linkbases if they have already been loaded once
            controller.addToLog(_("CSSF checks already loaded."))
            return
    lastReference = len(linkbaseReferences)-1
    for i, fileName in enumerate(linkbaseReferences.keys()):
        url = linkbaseReferences[fileName]
        if i==lastReference:
            fileOpenURL(url, modelXbrl, controller, reloadViews=True)
        else:
            fileOpenURL(url, modelXbrl, controller, reloadViews=False)

def identifyFileType(modelXbrl, rootNode, filepath):
    _class = ModelDocument.ModelDocument
    if os.path.basename(filepath) in linkbaseReferences:
        return (Type.LINKBASE, _class, rootNode)
    else:
        return (Type.UnknownXML, _class, rootNode)

def cssfToolsMenuExtender(cntlr, menu):
    # Extend menu with an item for the improve compliance menu
    menu.add_command(label=_("Load CSSF checks"), 
                     underline=0, 
                     command=lambda: loadAllCSSFFiles(cntlr) )

__pluginInfo__ = {
    # Do not use _( ) in pluginInfo itself (it is applied later, after loading
    'name': 'CSSF plausibility checks',
    'version': '1.2',
    'description': '''CSSF plausibility check in conformance with http://www.cssf.lu/fileadmin/files/Reporting_legal/Recueil_banques/CSSF_Plausibility_checks_Clean_version_260115.pdf.''',
    'license': 'Apache-2',
    'author': 'Acsone S. A.',
    'copyright': '(c) Copyright Acsone S. A., All rights reserved.',
    # classes of mount points (required)
    'ModelDocument.IdentifyType': identifyFileType,
    'CntlrWinMain.Menu.Tools': cssfToolsMenuExtender,
}
