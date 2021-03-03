import sys, os
sys.path.append("../core")          # files from the core
import adfisher                     # adfisher wrapper function
import web.pre_experiment.alexa     # collecting top sites from alexa
import web.google_news              # interacting with Google News
import web.google_ads
import converter.reader             # read log and create feature vectors
import analysis.statistics          # statistics for significance testing

log_file = 'log.politics.txt'
site_file = 'politics.txt'

def make_browser(unit_id, treatment_id):
    b = web.google_ads.GoogleAdsUnit(browser='chrome', log_file=log_file, unit_id=unit_id,
        treatment_id=treatment_id, headless=False, proxy = None)
    return b

# web.pre_experiment.alexa.collect_sites(make_browser, num_sites=5, output_file=site_file,
#     alexa_link="http://www.alexa.com/topsites")

# Control Group treatment
def control_treatment(unit):
    unit.login('chempto@gmail.com', '')
    #unit.opt_in()
    #unit.set_gender('m')
    unit.visit_sites(site_file='politics.txt')

# Experimental Group treatment
def exp_treatment(unit):
    #unit.opt_in()
    #unit.set_gender('m')
    unit.visit_sites(site_file='politicsR.txt')


# Measurement - Collects ads
def measurement(unit):
    unit.collect_ads(reloads=2, delay=5, site='bbc')


# Shuts down the browser once we are done with it.
def cleanup_browser(unit):
    unit.quit()

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

# Load results reads the log_file, and creates feature vectors
def load_results():
    collection, treat_names = converter.reader.read_log(log_file="log.politics.txt")
    return converter.reader.get_feature_vectors(collection, feat_choice='ads')

def test_stat(observed_values, unit_assignments):
    return analysis.statistics.difference(observed_values, unit_assignments)


adfisher.do_experiment(make_unit=make_browser, treatments=[control_treatment, exp_treatment],
                        measurement=measurement, end_unit=cleanup_browser,
                        load_results=load_results, test_stat=test_stat, ml_analysis=True,
                        num_blocks=20, num_units=4, timeout=2000,
                        log_file=log_file, exp_flag=True, analysis_flag=False,
                        treatment_names=["control (liberal)", "experimental(conservative)"])
