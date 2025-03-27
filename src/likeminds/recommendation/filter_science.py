import re
import pandas as pd

# Major scientific domains list
scientific_domains = [
    # Preprint servers
    'arxiv.org',
    'biorxiv.org',
    'medrxiv.org',
    'chemrxiv.org',
    'psyarxiv.org',
    'eartharxiv.org',
    'socarxiv.org',
    'osf.io',
    'preprints.org',
    'ssrn.com',
    'econstor.eu',
    
    # Major publishers
    'nature.com',
    'science.org',
    'sciencemag.org',
    'cell.com',
    'pnas.org',
    'springer.com',
    'springerlink.com',
    'link.springer.com',
    'wiley.com',
    'onlinelibrary.wiley.com',
    'tandfonline.com',
    'taylor-francis.com',
    'sciencedirect.com',
    'elsevier.com',
    'journals.elsevier.com',
    'academic.oup.com',
    'oup.com',
    'oxfordjournals.org',
    'oxfordacademic.org',
    'sage.com',
    'journals.sagepub.com',
    'sagepub.com',
    'bmj.com',
    'nejm.org',
    'acs.org',
    'pubs.acs.org',
    'rsc.org',
    'pubs.rsc.org',
    'ieee.org',
    'ieeexplore.ieee.org',
    'frontiersin.org',
    'mdpi.com',
    'plos.org',
    'journals.plos.org',
    'jama.com',
    'jamanetwork.com',
    'lancet.com',
    'thelancet.com',
    'annualreviews.org',
    'jstor.org',
    'acm.org',
    'dl.acm.org',
    'jamanetwork.com',
    'hindawi.com',
    'iospress.com',
    'spandidos-publications.com',
    'emerald.com',
    'emeraldinsight.com',
    'benthamscience.com',
    'worldscientific.com',
    'liebertpub.com',
    'futuremedicine.com',
    
    # University publishers
    'cambridge.org',
    'journals.cambridge.org',
    'press.princeton.edu',
    'press.uchicago.edu',
    'yale.edu/yup',
    'hup.harvard.edu',
    'mitpress.mit.edu',
    'sup.org',
    
    # Open access and institutional repositories
    'zenodo.org',
    'figshare.com',
    'doaj.org',
    'dovepress.com',
    'elifesciences.org',
    'biomedcentral.com',
    'bmcmedicine.com',
    'jmir.org',
    'cogentoa.com',
    
    # National institutions and databases
    'nih.gov',
    'ncbi.nlm.nih.gov',
    'pubmed.ncbi.nlm.nih.gov',
    'pmc.ncbi.nlm.nih.gov',
    'cdc.gov',
    'europa.eu',
    'jst.go.jp',
    'nist.gov',
    'nasa.gov',
    'osti.gov',
    'aip.org',
    'aps.org',
    'ams.org',
    
    # Identifiers and metrics
    'doi.org',
    'handle.net',
    'researchgate.net',
    'academia.edu',
    'scopus.com',
    'webofscience.com',
    'semanticscholar.org',
    'orcid.org',
    
    # Field-specific repositories
    'repec.org',
    'ideas.repec.org',
    'arxiv-vanity.com',
    'dblp.org',
    'inspirehep.net',
    'spie.org',
    'computer.org',
    'projecteuclid.org',
    'astro.caltech.edu',
    'geoscienceworld.org',
    'geologicalsociety.org.uk',
    
    # Society publishers
    'agu.org',
    'asme.org',
    'asce.org',
    'asm.org',
    'geosociety.org',
    'ametsoc.org',
    'geological-society.org.uk',
    'royalsociety.org',
    'royalsocietypublishing.org',
    'faseb.org',
    'asbmb.org',
    'apsnet.org',
    'aaas.org',
    'aip.scitation.org',
    
    # Country-specific journals
    'cnki.net',
    'csiro.au',
    'jstage.jst.go.jp',
    'scielo.org',
    'nrc-cnrc.gc.ca',
    'koreascience.or.kr',
    'cairn.info',
    'sciencespo.fr',
    'recyt.fecyt.es',
    
    # Medical journals and databases
    'thelancet.com',
    'bmj.com',
    'jamanetwork.com',
    'nejm.org',
    'jci.org',
    'blood.org',
    'amjmed.com',
    'annals.org',
    'abstractsonline.com',
    'medscape.com',
    
    # Citation managers/research tools
    'mendeley.com',
    'zotero.org',
    'endnote.com',
    'paperpile.com',
    'overleaf.com'
]

def is_scientific_url(url):
    """Check if a URL is from a scientific domain"""
    import re
    from urllib.parse import urlparse
    
    # For case like links to DOIs directly
    if re.search(r'doi\.org/10\.\d{4,9}/[-._;()/:A-Z0-9]+', url):
        return True
        
    # Extract domain from URL
    try:
        domain = urlparse(url).netloc.lower()
        if not domain:
            return False
            
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # Check against scientific domains list
        for scientific_domain in scientific_domains:
            if domain == scientific_domain or domain.endswith('.' + scientific_domain):
                return True
                
        # Look for patterns indicating scholarly content
        paper_patterns = [
            r'/pdf/[^/]+\.pdf$',  # PDF link
            r'/doi/(?:abs|full|pdf)/10\.\d{4,9}/', # DOI in URL path
            r'/article/\d+',  # Article with ID
            r'/content/\d+/\d+/\w+', # Content with issue number
            r'/science/article/pii/\w+', # Elsevier PII
            r'/pmid/\d+', # PubMed ID
            r'/pmc/articles/PMC\d+', # PubMed Central
            r'/abstract/\d+', # Abstract with ID
            r'/full/\d+', # Full text with ID
        ]
        
        for pattern in paper_patterns:
            if re.search(pattern, url):
                return True
                
        return False
        
    except Exception:
        return False


def is_scientific_keywords(text: str) -> bool:
    """
    A function to identify whether a text 
    appears to be scientific in nature based on keywords.
    """
    import re
    science_keywords = [
        r'\bscience\b',
        r'\bresearch\b',
        r'\bstudy\b',
        r'\bexperiment\b',
        r'\bdata\b',
        r'\bphd\b',
        r'\bpublication\b',
        r'\bscientific\b',
    ]
    pattern = re.compile('|'.join(science_keywords), re.IGNORECASE)
    return bool(pattern.search(text))

def is_scientific_post(text: str) -> bool:
    """
    Determines if a post is scientific by checking:
    1. If the post text contains scientific keywords.
    2. If any URLs in the post text are from known scientific domains.
    """
    import re
    
    # Check for scientific keywords
    if is_scientific_keywords(text):
        return True
    
    # Extract URLs from the text
    urls = re.findall(r'https?://\S+', text)
    for url in urls:
        if is_scientific_url(url):
            return True
            
    return False

def add_is_scientific_column(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """
    Adds a boolean column 'is_scientific' to a DataFrame of posts, 
    based on the content in the specified text column.
    
    The function parses the post text for scientific keywords and URLs,
    then determines if the post is scientific.
    
    :param df: DataFrame containing post data.
    :param text_column: Name of the column in df that stores post text.
    :return: DataFrame with a new 'is_scientific' column.
    """
    df['is_scientific'] = df[text_column].apply(is_scientific_post)
    return df

def filter_posts_by_science(df: pd.DataFrame, keep_scientific: bool = True) -> pd.DataFrame:
    """
    Returns a subset of the DataFrame containing only scientific posts 
    (if keep_scientific=True), or non-scientific posts otherwise.
    
    :param df: DataFrame 
    :param keep_scientific: True => keep only posts where 'is_scientific' == True.
    :return: Filtered DataFrame.
    """
    df = add_is_scientific_column(df, "text")
    return df[df['is_scientific'] == keep_scientific]

'''
test_urls = [
    "https://www.nature.com/articles/s41586-021-03819-2",
    "https://science.org/doi/10.1126/science.abc1234",
    "https://cnn.com/news/article",
    "https://arxiv.org/abs/2103.05247",
    "https://doi.org/10.1038/d41586-020-00502-w",
    "https://www.sciencedirect.com/science/article/pii/S0140673620301835",
    "https://www.biorxiv.org/content/10.1101/2020.02.07.939389v1",
    "https://pubmed.ncbi.nlm.nih.gov/32182409/",
    "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(20)30183-5/fulltext",
]

for url in test_urls:
    result = is_scientific_url(url)
    print(result)
'''
