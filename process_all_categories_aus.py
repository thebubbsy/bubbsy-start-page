import json
import os
import re

def clean_domain(url):
    if not url:
        return ""
    try:
        domain = re.sub(r'^https?:\/\/', '', url)
        domain = domain.split('/')[0].split('?')[0].split(':')[0]
        return domain.lower()
    except Exception:
        return ""

# Comprehensive dictionary of Australian OSINT tools mapped to widget titles / categories
AUS_CATEGORY_MAP = {
    # 1. THROWAWAY / TEMP CONTACTS / SMS
    'THROWAWAY CONTACT': [
        {'title': '[AUS] Receive-SMS Australia (+61)', 'url': 'https://receive-sms.cc/Australia-Phone-Number/', 'description': 'Free disposable Australian +61 numbers for SMS verification', 'domain': 'receive-sms.cc'},
        {'title': '[AUS] Quackr Australia Temp Number', 'url': 'https://quackr.io/temporary-numbers/australia', 'description': 'Temporary Australian phone numbers for instant OTP verification', 'domain': 'quackr.io'},
        {'title': '[AUS] AnonymSMS (+61 Australia)', 'url': 'https://anonymsms.com/temporary-phone-number/australia/', 'description': 'Free online disposable mobile numbers in Australia', 'domain': 'anonymsms.com'},
        {'title': '[AUS] Crazytel Australia (VOIP & SMS)', 'url': 'https://crazytel.com.au/', 'description': 'Low cost Australian DID numbers, burner SIP trunks, and SMS routing', 'domain': 'crazytel.com.au'}
    ],

    # 2. ID GENERATOR / FAKE DETAILS
    'ID GENERATOR': [
        {'title': '[AUS] Fake Address Generator Australia', 'url': 'https://www.fakeaddressgenerator.com/World/Australia_address_generator', 'description': 'Generate Australian addresses, suburbs, postcodes, and phone numbers', 'domain': 'fakeaddressgenerator.com'},
        {'title': '[AUS] Australia Post Postcode & Address Finder', 'url': 'https://auspost.com.au/postcode', 'description': 'Official Australia Post suburb, postcode, and delivery address validator', 'domain': 'auspost.com.au'},
        {'title': '[AUS] Fake Detail Australia Generator', 'url': 'https://fakedetail.com/fake-address-generator/australia', 'description': 'Generate synthetic Australian identities, TFN formats, and credentials', 'domain': 'fakedetail.com'}
    ],

    # 3. WEATHER / RADAR
    'WEATHER': [
        {'title': '[AUS] BOM (Bureau of Meteorology)', 'url': 'http://www.bom.gov.au/', 'description': 'Official Australian national weather service, Doppler rain radars, and satellite imagery', 'domain': 'bom.gov.au'},
        {'title': '[AUS] Weatherzone Australia', 'url': 'https://www.weatherzone.com.au/', 'description': 'High-resolution Australian radar, lightning tracker, and synoptic charts', 'domain': 'weatherzone.com.au'},
        {'title': '[AUS] WillyWeather Australia', 'url': 'https://www.willyweather.com.au/', 'description': 'Hyper-local Australian wind, tide, swell, UV, and rainfall reports', 'domain': 'willyweather.com.au'},
        {'title': '[AUS] BoM Marine & Ocean Weather', 'url': 'http://www.bom.gov.au/marine/', 'description': 'Australian coastal waters forecasts, gale warnings, and sea surface temperatures', 'domain': 'bom.gov.au'}
    ],

    # 4. THREAT INTEL / CYBER / OPSEC
    'THREAT INTEL': [
        {'title': '[AUS] ACSC (Australian Cyber Security Centre)', 'url': 'https://www.cyber.gov.au/', 'description': 'Official Australian signals directorate threat advisories, alerts, and incident reporting', 'domain': 'cyber.gov.au'},
        {'title': '[AUS] AusCERT Security Incident Response', 'url': 'https://auscert.org.au/', 'description': 'Australian Computer Emergency Response Team security alerts and vulnerability notices', 'domain': 'auscert.org.au'},
        {'title': '[AUS] OAIC Notifiable Data Breaches', 'url': 'https://www.oaic.gov.au/privacy/notifiable-data-breaches', 'description': 'Reports and statistics on mandatory privacy data breaches in Australia', 'domain': 'oaic.gov.au'},
        {'title': '[AUS] Have I Been Pwned (Troy Hunt - AU)', 'url': 'https://haveibeenpwned.com/', 'description': 'Gold Coast based global data breach indexing service created by Troy Hunt', 'domain': 'haveibeenpwned.com'}
    ],

    # 5. PRIVACY / SECURITY
    'PRIVACY / SECURITY': [
        {'title': '[AUS] OAIC Privacy Commissioner Guidelines', 'url': 'https://www.oaic.gov.au/privacy', 'description': 'Australian Privacy Principles (APPs), surveillance law, and data access rights', 'domain': 'oaic.gov.au'},
        {'title': '[AUS] Electronic Frontiers Australia (EFA)', 'url': 'https://www.efa.org.au/', 'description': 'Australian digital rights, mandatory data retention opposition, and surveillance analysis', 'domain': 'efa.org.au'},
        {'title': '[AUS] IDCARE (National Identity Support AU)', 'url': 'https://www.idcare.org/', 'description': 'Australia national identity and cyber support service for credential compromise', 'domain': 'idcare.org'}
    ],

    # 6. RESOLVERS / ANALYTICS
    'RESOLVERS': [
        {'title': '[AUS] auDA Registrar & Registry Resolution', 'url': 'https://www.auda.org.au/', 'description': 'Official .au domain registrar status and registrant policy verification', 'domain': 'auda.org.au'},
        {'title': '[AUS] Aussie Broadband Looking Glass', 'url': 'https://looking-glass.aussiebroadband.com.au/', 'description': 'Australian BGP routing, ping, and traceroute diagnostic endpoint', 'domain': 'aussiebroadband.com.au'}
    ],
    'ANALYTICS': [
        {'title': '[AUS] Similarweb Australia Rankings', 'url': 'https://www.similarweb.com/top-websites/australia/', 'description': 'Top visited web domains and traffic analytics across Australia', 'domain': 'similarweb.com'},
        {'title': '[AUS] ABS Australian Industry Statistics', 'url': 'https://www.abs.gov.au/statistics/industry', 'description': 'Statistical market share and digital economy metrics for Australia', 'domain': 'abs.gov.au'}
    ],

    # 7. UNIFIED SEARCH & PEOPLE SEARCH
    'UNIFIED SEARCH': [
        {'title': '[AUS] Google Australia Custom Search', 'url': 'https://www.google.com.au/', 'description': 'Google search localized to Australian servers and regional index', 'domain': 'google.com.au'},
        {'title': '[AUS] Trove All-in-One Australian Search', 'url': 'https://trove.nla.gov.au/', 'description': 'Unified discovery across Australian newspapers, archives, books, and gazettes', 'domain': 'trove.nla.gov.au'}
    ],
    'PEOPLE': [
        {'title': '[AUS] White Pages Australia (Residential)', 'url': 'https://www.whitepages.com.au/', 'description': 'Australia premier residential phone numbers, names, and address directory', 'domain': 'whitepages.com.au'},
        {'title': '[AUS] Ryerson Index (Australian Death Notices)', 'url': 'https://www.ryersonindex.org/', 'description': '8.5M+ indexed notices from Australian newspapers for people tracing', 'domain': 'ryersonindex.org'},
        {'title': '[AUS] AEC Electoral Enrolment Check', 'url': 'https://check.aec.gov.au/', 'description': 'Verify if an Australian resident is registered on the electoral roll', 'domain': 'aec.gov.au'},
        {'title': '[AUS] Truecaller Australia (+61)', 'url': 'https://www.truecaller.com/', 'description': 'Search Australian names and caller IDs linked to +61 mobile and landline numbers', 'domain': 'truecaller.com'}
    ],
    'USERNAME': [
        {'title': '[AUS] Whirlpool Forums User Search', 'url': 'https://forums.whirlpool.net.au/user/', 'description': 'Search profiles and history on Australia largest tech and lifestyle community', 'domain': 'whirlpool.net.au'},
        {'title': '[AUS] OzBargain Member Lookup', 'url': 'https://www.ozbargain.com.au/user/', 'description': 'Search usernames and activity on Australia leading consumer forum', 'domain': 'ozbargain.com.au'},
        {'title': '[AUS] Gumtree Australia User Profiles', 'url': 'https://www.gumtree.com.au/', 'description': 'Search sellers, listings, and user identifiers across Australia', 'domain': 'gumtree.com.au'}
    ],
    'EMAIL': [
        {'title': '[AUS] Australian Domain MX / Email Checker', 'url': 'https://mxtoolbox.com/domain/com.au', 'description': 'Inspect mail exchange records and SPF/DKIM for Australian .au domains', 'domain': 'mxtoolbox.com'},
        {'title': '[AUS] Telstra BigPond / Optus Mail Host Check', 'url': 'https://mxtoolbox.com/SuperTool.aspx', 'description': 'Query major Australian ISP email gateways (bigpond, optusnet, tpg, iinet)', 'domain': 'mxtoolbox.com'}
    ],
    'PHONE': [
        {'title': '[AUS] Reverse Australia (Phone Lookup)', 'url': 'https://www.reverseaustralia.com/', 'description': 'Australia leading reverse phone directory with caller feedback and addresses', 'domain': 'reverseaustralia.com'},
        {'title': '[AUS] ACMA Numbering Register Lookup', 'url': 'https://www.thenumberingsystem.com.au/', 'description': 'Find which Australian carrier (Telstra, Optus, TPG) was allocated any phone prefix', 'domain': 'thenumberingsystem.com.au'},
        {'title': '[AUS] ACMA Do Not Call Register', 'url': 'https://www.donotcall.gov.au/', 'description': 'Australian telecommunications consumer register and marketing compliance rules', 'domain': 'donotcall.gov.au'},
        {'title': '[AUS] Yellow Pages Australia Phone Directory', 'url': 'https://www.yellowpages.com.au/', 'description': 'Lookup commercial Australian phone numbers, direct lines, and departments', 'domain': 'yellowpages.com.au'}
    ],

    # 8. SOCIAL MEDIA (Reddit, Twitter, Facebook, YouTube AU)
    'REDDIT': [
        {'title': '[AUS] /r/australia Subreddit', 'url': 'https://www.reddit.com/r/australia/new/', 'description': 'Australia primary national discussion community and breaking news', 'domain': 'reddit.com'},
        {'title': '[AUS] /r/AusFinance Community', 'url': 'https://www.reddit.com/r/AusFinance/new/', 'description': 'Australian economic trends, property discussion, and financial intelligence', 'domain': 'reddit.com'},
        {'title': '[AUS] /r/AusLegal Community', 'url': 'https://www.reddit.com/r/AusLegal/new/', 'description': 'Discussions on Australian federal and state law, police, and legal disputes', 'domain': 'reddit.com'}
    ],
    'NEWS': [
        {'title': '[AUS] ABC News Australia (Live)', 'url': 'https://www.abc.net.au/news', 'description': 'Australian national broadcaster live news, investigations, and four corners reports', 'domain': 'abc.net.au'},
        {'title': '[AUS] SBS News World & Australia', 'url': 'https://www.sbs.com.au/news', 'description': 'Special Broadcasting Service Australian and multicultural news portal', 'domain': 'sbs.com.au'},
        {'title': '[AUS] Australian Financial Review (AFR)', 'url': 'https://www.afr.com/', 'description': 'Australia premier business, corporate governance, and markets intelligence', 'domain': 'afr.com'},
        {'title': '[AUS] The Guardian Australia', 'url': 'https://www.theguardian.com/au', 'description': 'Independent investigative journalism and political analysis in Australia', 'domain': 'theguardian.com'}
    ],

    # 9. SEARCH ENGINES / GOOGLE CSE / DORKING
    'SEARCH ENGINES': [
        {'title': '[AUS] Google Australia (.com.au)', 'url': 'https://www.google.com.au/', 'description': 'Google search prioritizing Australian regional results and local servers', 'domain': 'google.com.au'},
        {'title': '[AUS] Trove Newspapers Search', 'url': 'https://trove.nla.gov.au/newspaper/', 'description': 'National Library of Australia digitized historical press search', 'domain': 'trove.nla.gov.au'},
        {'title': '[AUS] AusLII Comprehensive Legal Search', 'url': 'https://www.austlii.edu.au/', 'description': 'Search all Australian high, federal, and state courts and statutory rules', 'domain': 'austlii.edu.au'}
    ],
    'DORKING': [
        {'title': '[AUS] Google Dork: Australian Gov Documents', 'url': 'https://www.google.com/search?q=site:gov.au+filetype:pdf', 'description': 'Find public PDF documents, disclosures, and reports hosted on .gov.au domains', 'domain': 'google.com'},
        {'title': '[AUS] Google Dork: Australian FOI Disclosures', 'url': 'https://www.google.com/search?q=site:gov.au+%22Freedom+of+Information%22+OR+%22FOI+Disclosure+Log%22', 'description': 'Discover unindexed FOI releases from Australian federal and state agencies', 'domain': 'google.com'},
        {'title': '[AUS] Google Dork: Australian University Repositories', 'url': 'https://www.google.com/search?q=site:edu.au+filetype:pdf+OR+filetype:xlsx', 'description': 'Search Australian university research repositories and data files', 'domain': 'google.com'}
    ],
    'OPEN DIRECTORY': [
        {'title': '[AUS] data.gov.au Open Datasets', 'url': 'https://data.gov.au/', 'description': '10,000+ open public datasets across Australian Commonwealth and State bodies', 'domain': 'data.gov.au'},
        {'title': '[AUS] National Archives of Australia Public Files', 'url': 'https://www.naa.gov.au/explore-collection', 'description': 'Declassified Australian intelligence, defense, and passenger archives', 'domain': 'naa.gov.au'},
        {'title': '[AUS] Australian Data Archive (ADA)', 'url': 'https://ada.edu.au/', 'description': 'Social, political, and demographic open datasets hosted at ANU', 'domain': 'ada.edu.au'}
    ],

    # 10. DOMAIN / IP / DNS / WHOIS
    'WHOIS': [
        {'title': '[AUS] auDA Official WHOIS (.au Domains)', 'url': 'https://www.auda.org.au/tools/whois', 'description': 'Official registrar and registrant entity lookup for .com.au, .net.au, and .au domains', 'domain': 'auda.org.au'},
        {'title': '[AUS] APNIC WHOIS (Asia-Pacific IP Registry)', 'url': 'https://wq.apnic.net/static/search.html', 'description': 'Regional Internet Registry for Australia - lookup IP blocks, ASNs, and network owners', 'domain': 'apnic.net'}
    ],
    'DOMAIN / IP / DNS': [
        {'title': '[AUS] auDA WHOIS Search', 'url': 'https://www.auda.org.au/tools/whois', 'description': 'Lookup Australian domain registrant ABN/ACN and authorized contact details', 'domain': 'auda.org.au'},
        {'title': '[AUS] APNIC IP & ASN Routing Database', 'url': 'https://wq.apnic.net/', 'description': 'IP address allocations and Autonomous System Numbers for Australian ISPs', 'domain': 'apnic.net'},
        {'title': '[AUS] Telstra Looking Glass & BGP Route Server', 'url': 'https://telstra.net/lookingglass', 'description': 'Telstra national backbone routing and BGP path analysis', 'domain': 'telstra.net'}
    ],

    # 11. LICENSE PLATE / VIN / VEHICLE
    'LICENSE PLATE / VIN / VEHICLE': [
        {'title': '[AUS] PPSR (Personal Property Securities Register)', 'url': 'https://www.ppsr.gov.au/', 'description': 'Search any Australian vehicle VIN for security interests, written-off status, and theft', 'domain': 'ppsr.gov.au'},
        {'title': '[AUS] Service NSW Vehicle Rego Check', 'url': 'https://www.service.nsw.gov.au/transaction/check-a-vehicle-registration', 'description': 'Free NSW license plate rego status, CTP insurer, and expiry date lookup', 'domain': 'service.nsw.gov.au'},
        {'title': '[AUS] VicRoads Vehicle Registration Check', 'url': 'https://www.vicroads.vic.gov.au/registration/buy-sell-or-transfer-a-vehicle/check-vehicle-registration/vehicle-registration-enquiry', 'description': 'Free Victorian vehicle registration and VIN verification tool', 'domain': 'vicroads.vic.gov.au'},
        {'title': '[AUS] QLD Transport Vehicle Rego Check', 'url': 'https://www.service.transport.qld.gov.au/checkrego/application/VehicleSearch.xhtml', 'description': 'Queensland vehicle registration and plate verification', 'domain': 'service.transport.qld.gov.au'},
        {'title': '[AUS] RegoCheck.com.au (All States AU)', 'url': 'https://www.regocheck.com.au/', 'description': 'Free unified license plate checker covering NSW, VIC, QLD, WA, SA, TAS, ACT, NT', 'domain': 'regocheck.com.au'},
        {'title': '[AUS] RedBook Australia (Vehicle Specs & Valuation)', 'url': 'https://www.redbook.com.au/', 'description': 'Lookup Australian vehicle models, badge trims, factory options, and price histories', 'domain': 'redbook.com.au'}
    ],

    # 12. FLIGHT TRACKER / MARITIME
    'FLIGHT TRACKER': [
        {'title': '[AUS] CASA (Civil Aircraft Register Australia)', 'url': 'https://www.casa.gov.au/aircraft/register-aircraft/civil-aircraft-register', 'description': 'Search all VH- registered Australian aircraft, airframe details, and registered owners', 'domain': 'casa.gov.au'},
        {'title': '[AUS] Airservices Australia (WebTrak Flight Paths)', 'url': 'https://www.airservicesaustralia.com/community/flight-path-information/webtrak/', 'description': 'Live tracking and noise monitoring of flights across major Australian airports', 'domain': 'airservicesaustralia.com'},
        {'title': '[AUS] FlightAware Australia Airspace', 'url': 'https://www.flightaware.com/live/region/Australia', 'description': 'Real-time flight tracking across Australian FIR airspace and airports', 'domain': 'flightaware.com'}
    ],
    'MARITIME': [
        {'title': '[AUS] AMSA (Australian Register of Ships)', 'url': 'https://www.amsa.gov.au/vessels-operators/ship-registration/australian-register-ships', 'description': 'Official Australian maritime shipping register, commercial vessel owners, and tonnage', 'domain': 'amsa.gov.au'},
        {'title': '[AUS] MarineTraffic Australia AIS Tracking', 'url': 'https://www.marinetraffic.com/en/ais/home/centerx/145.0/centery/-30.0/zoom/4', 'description': 'Live satellite and coastal AIS tracking for ships in Australian waters and ports', 'domain': 'marinetraffic.com'},
        {'title': '[AUS] Port Authority of NSW Vessel Movements', 'url': 'https://www.portauthoritynsw.com.au/', 'description': 'Daily arrivals and departures for Sydney Harbour, Port Botany, and Port Kembla', 'domain': 'portauthoritynsw.com.au'}
    ],

    # 13. IoT / RADIO / SPECTRUM
    'IoT': [
        {'title': '[AUS] ACMA Radcom Spectrum Register (IoT / RF)', 'url': 'https://web.acma.gov.au/rrl/', 'description': 'Search all licensed wireless, cellular, and IoT transmitter sites in Australia', 'domain': 'acma.gov.au'},
        {'title': '[AUS] Shodan Australia (.au / country:AU)', 'url': 'https://www.shodan.io/search?query=country:AU', 'description': 'Search indexed IoT hardware, webcams, SCADA, and servers located in Australia', 'domain': 'shodan.io'}
    ],
    'RADIO': [
        {'title': '[AUS] ACMA Register of Radiocommunications Licences (RRL)', 'url': 'https://web.acma.gov.au/rrl/', 'description': 'Official database of all radio frequencies, tower coordinates, and license holders in AU', 'domain': 'acma.gov.au'},
        {'title': '[AUS] RadioReference Australia (Scanner Frequencies)', 'url': 'https://www.radioreference.com/db/browse/coid/14', 'description': 'Police, emergency services, aviation, and marine radio scanner frequencies for AU', 'domain': 'radioreference.com'},
        {'title': '[AUS] Broadcast Australia Transmitter Map', 'url': 'https://www.baxtel.com/search?country=Australia', 'description': 'Terrestrial radio, AM/FM, and digital television transmission towers in Australia', 'domain': 'baxtel.com'}
    ],

    # 14. REAL ESTATE / MAPS / GEO
    'REAL ESTATE': [
        {'title': '[AUS] Realestate.com.au', 'url': 'https://www.realestate.com.au/', 'description': 'Search Australian residential, commercial property histories, floorplans, and sales', 'domain': 'realestate.com.au'},
        {'title': '[AUS] Domain.com.au Property Records', 'url': 'https://www.domain.com.au/', 'description': 'Property price estimates, sold histories, zoning, and auction results in Australia', 'domain': 'domain.com.au'},
        {'title': '[AUS] PropertyValue Australia (CoreLogic Data)', 'url': 'https://www.propertyvalue.com.au/', 'description': 'CoreLogic Australian property sales history, estimated value, and title data', 'domain': 'propertyvalue.com.au'}
    ],
    'MAPS': [
        {'title': '[AUS] NSW SIX Maps (Spatial Information Exchange)', 'url': 'https://maps.six.nsw.gov.au/', 'description': 'NSW high-res cadastral mapping, property lot/DP boundaries, and historical aerials', 'domain': 'six.nsw.gov.au'},
        {'title': '[AUS] VicPlan (Victoria Planning & Land Zones)', 'url': 'https://mapshare.vic.gov.au/vicplan/', 'description': 'Victorian property boundaries, planning zones, overlays, and council permits', 'domain': 'mapshare.vic.gov.au'},
        {'title': '[AUS] Queensland Globe (Cadastre & Satellite)', 'url': 'https://qldglobe.information.qld.gov.au/', 'description': 'Interactive satellite imagery, land parcel boundaries, and property data for QLD', 'domain': 'information.qld.gov.au'},
        {'title': '[AUS] Geoscience Australia NationalMap', 'url': 'https://nationalmap.gov.au/', 'description': 'National Australian geospatial data, infrastructure, satellite imagery, and topography', 'domain': 'nationalmap.gov.au'},
        {'title': '[AUS] ACTmapi (Canberra & ACT Spatial Maps)', 'url': 'https://www.actmapi.act.gov.au/', 'description': 'ACT cadastral maps, zoning, land titles, and public infrastructure', 'domain': 'actmapi.act.gov.au'}
    ],
    'GEO': [
        {'title': '[AUS] Geoscience Australia Geodesy & Imagery', 'url': 'https://www.ga.gov.au/', 'description': 'Australian geological maps, seismic data, satellite Earth observation, and elevation', 'domain': 'ga.gov.au'},
        {'title': '[AUS] Nearmap Australia (High-Res Aerials)', 'url': 'https://www.nearmap.com/au/en', 'description': 'Frequently updated sub-5cm aerial photogrammetry for Australian urban centers', 'domain': 'nearmap.com'}
    ],

    # 15. CRYPTOCURRENCY / FINANCE / BUSINESS
    'CRYPTOCURRENCY': [
        {'title': '[AUS] AUSTRAC Digital Currency Exchange Register', 'url': 'https://www.austrac.gov.au/business/industry/digital-currency-exchange-providers', 'description': 'List of regulated and registered cryptocurrency exchanges operating in Australia', 'domain': 'austrac.gov.au'},
        {'title': '[AUS] CoinJar & CoinSpot Australia Markets', 'url': 'https://www.coinspot.com.au/', 'description': 'Australian domestic cryptocurrency trading volumes and AUD order books', 'domain': 'coinspot.com.au'}
    ],
    'FINANCE': [
        {'title': '[AUS] ASX (Australian Securities Exchange)', 'url': 'https://www.asx.com.au/', 'description': 'Australian stock quotes, executive filings, market disclosures, and financial reports', 'domain': 'asx.com.au'},
        {'title': '[AUS] RBA (Reserve Bank of Australia Economic Data)', 'url': 'https://www.rba.gov.au/statistics/', 'description': 'Australian monetary policy, exchange rates, banking aggregates, and inflation data', 'domain': 'rba.gov.au'},
        {'title': '[AUS] APRA Regulated Financial Institutions', 'url': 'https://www.apra.gov.au/register-of-authorised-deposit-taking-institutions', 'description': 'Australian Prudential Regulation Authority list of authorized banks, ADIs, and insurers', 'domain': 'apra.gov.au'}
    ],
    'BUSINESS': [
        {'title': '[AUS] ABN Lookup (Australian Business Register)', 'url': 'https://abr.business.gov.au/', 'description': 'Search Australian Business Numbers, GST status, business names, and trading entities', 'domain': 'business.gov.au'},
        {'title': '[AUS] ASIC Connect (Company & Business Register)', 'url': 'https://connectonline.asic.gov.au/', 'description': 'Search Australian company directors, registered office, ACN, and document filings', 'domain': 'asic.gov.au'},
        {'title': '[AUS] AFSA Bankruptcy Register (NPII)', 'url': 'https://www.afsa.gov.au/', 'description': 'National Personal Insolvency Index - check bankruptcy and insolvency records in Australia', 'domain': 'afsa.gov.au'},
        {'title': '[AUS] IP Australia (Trade Marks Search - ATMOSS)', 'url': 'https://search.ipaustralia.gov.au/trademarks/search/quick', 'description': 'Search registered Australian trade marks, patent holders, and commercial IP owners', 'domain': 'ipaustralia.gov.au'},
        {'title': '[AUS] ACNC (Australian Charities Register)', 'url': 'https://www.acnc.gov.au/charity/charities', 'description': 'Search registered charities, board members, financial reports, and non-profits', 'domain': 'acnc.gov.au'}
    ],

    # 16. POLICE / LE / FED / COURTS / GOV / PUBLIC RECORDS
    'POLICE / LE / FED': [
        {'title': '[AUS] Australian Federal Police (AFP)', 'url': 'https://www.afp.gov.au/', 'description': 'National policing, wanted persons, cybercrime alerts, and federal investigations', 'domain': 'afp.gov.au'},
        {'title': '[AUS] Crime Stoppers Australia', 'url': 'https://crimestoppers.com.au/', 'description': 'National unsolved crime appeals, fugitive lists, and anonymous reporting', 'domain': 'crimestoppers.com.au'},
        {'title': '[AUS] ACIC (Australian Criminal Intelligence Commission)', 'url': 'https://www.acic.gov.au/', 'description': 'Australia national criminal intelligence agency and illicit market reports', 'domain': 'acic.gov.au'},
        {'title': '[AUS] NSW Police Force Wanted & News', 'url': 'https://www.police.nsw.gov.au/', 'description': 'NSW Police media releases, wanted persons, and incident reports', 'domain': 'police.nsw.gov.au'},
        {'title': '[AUS] Victoria Police News & Wanted', 'url': 'https://www.police.vic.gov.au/', 'description': 'VicPol incident reports, crime appeals, and public notices', 'domain': 'police.vic.gov.au'},
        {'title': '[AUS] Queensland Police Service (QPS News)', 'url': 'https://mypolice.qld.gov.au/', 'description': 'Queensland Police news, stolen vehicle alerts, and public appeals', 'domain': 'police.qld.gov.au'},
        {'title': '[AUS] Western Australia Police Force', 'url': 'https://www.police.wa.gov.au/', 'description': 'WA Police crime alerts, wanted persons, and court listings', 'domain': 'police.wa.gov.au'}
    ],
    'VOTER DATABASES': [
        {'title': '[AUS] AEC (Australian Electoral Commission Check)', 'url': 'https://check.aec.gov.au/', 'description': 'Verify voter enrolment status, electorate boundaries, and political donation disclosures', 'domain': 'aec.gov.au'},
        {'title': '[AUS] AEC Transparency Register (Political Donations)', 'url': 'https://transparency.aec.gov.au/', 'description': 'Search declared political donations, party funding, and campaign expenditure in Australia', 'domain': 'aec.gov.au'},
        {'title': '[AUS] NSW Electoral Commission Disclosures', 'url': 'https://elections.nsw.gov.au/', 'description': 'NSW state election candidate disclosures, third-party campaigners, and registered voters', 'domain': 'elections.nsw.gov.au'}
    ],
    'PUBLIC RECORDS': [
        {'title': '[AUS] National Archives of Australia (RecordSearch)', 'url': 'https://recordsearch.naa.gov.au/', 'description': 'Search federal government files, immigration passenger lists, security dossiers, and defense records', 'domain': 'naa.gov.au'},
        {'title': '[AUS] Trove (National Library of Australia)', 'url': 'https://trove.nla.gov.au/', 'description': 'Digitized historic Australian newspapers (1803-present), gazettes, photos, and archives', 'domain': 'trove.nla.gov.au'},
        {'title': '[AUS] AusLII (Australasian Legal Information Institute)', 'url': 'https://www.austlii.edu.au/', 'description': 'High Court, Federal Court, Supreme Court judgments and legislation database', 'domain': 'austlii.edu.au'},
        {'title': '[AUS] Ryerson Index (Death & Funeral Notices)', 'url': 'https://www.ryersonindex.org/', 'description': '8.5M+ indexed notices from Australian newspapers for people tracing', 'domain': 'ryersonindex.org'},
        {'title': '[AUS] White Pages Australia (Residential Lookup)', 'url': 'https://www.whitepages.com.au/', 'description': 'Australia residential phone numbers, addresses, and contacts', 'domain': 'whitepages.com.au'},
        {'title': '[AUS] Findmypast Australia & New Zealand', 'url': 'https://www.findmypast.com.au/', 'description': 'Australian electoral rolls, census records, convict lists, and military service files', 'domain': 'findmypast.com.au'}
    ],
    'GOVERNMENT': [
        {'title': '[AUS] Federal Register of Legislation', 'url': 'https://www.legislation.gov.au/', 'description': 'Complete repository of Australian Commonwealth Acts, Regulations, and Gazettes', 'domain': 'legislation.gov.au'},
        {'title': '[AUS] data.gov.au (Australian Open Data)', 'url': 'https://data.gov.au/', 'description': 'Central portal for public datasets published by Australian government agencies', 'domain': 'data.gov.au'},
        {'title': '[AUS] AusTender (Government Procurement Contracts)', 'url': 'https://www.tenders.gov.au/', 'description': 'All Commonwealth procurement contracts, tender notices, and supplier expenditure', 'domain': 'tenders.gov.au'},
        {'title': '[AUS] Australian Parliament House (APH Directory)', 'url': 'https://www.aph.gov.au/Senators_and_Members', 'description': 'Directory of Senators, MPs, parliamentary declarations, and Hansard transcripts', 'domain': 'aph.gov.au'},
        {'title': '[AUS] Australian Bureau of Statistics (ABS Data)', 'url': 'https://www.abs.gov.au/', 'description': 'Census data, regional population profiles, economic indicators, and trade statistics', 'domain': 'abs.gov.au'},
        {'title': '[AUS] Transparency Portal (Australian Gov Reports)', 'url': 'https://www.transparency.gov.au/', 'description': 'Annual reports and performance data across Australian government bodies', 'domain': 'transparency.gov.au'}
    ],
    'SEX OFFENDER': [
        {'title': '[AUS] ACIC National Child Offender System (ANCOR)', 'url': 'https://www.acic.gov.au/services/national-child-offender-system', 'description': 'Australian national inter-jurisdictional register of reportable sex offenders', 'domain': 'acic.gov.au'},
        {'title': '[AUS] NSW Child Protection Register Reporting', 'url': 'https://www.police.nsw.gov.au/crime/child_protection_registry', 'description': 'NSW Police child protection registry enforcement and compliance notices', 'domain': 'police.nsw.gov.au'},
        {'title': '[AUS] Australian Institute of Criminology Reports', 'url': 'https://www.aic.gov.au/', 'description': 'National research on sexual violence, offender recidivism, and justice data in AU', 'domain': 'aic.gov.au'}
    ],
    'INFORMANT': [
        {'title': '[AUS] Crime Stoppers Australia (Anonymous Reporting)', 'url': 'https://crimestoppers.com.au/', 'description': 'National anonymous crime reporting, rewards, and intelligence submission portal', 'domain': 'crimestoppers.com.au'},
        {'title': '[AUS] High Court of Australia Transcripts & Submissions', 'url': 'https://www.hcourt.gov.au/cases/cases-transcripts', 'description': 'Transcripts and filings for High Court appeals, witness evidence, and legal argument', 'domain': 'hcourt.gov.au'}
    ],
    'RESIDENT DATABASE': [
        {'title': '[AUS] White Pages Australia (Residential Records)', 'url': 'https://www.whitepages.com.au/', 'description': 'Search Australian residential landlines, family names, and verified street addresses', 'domain': 'whitepages.com.au'},
        {'title': '[AUS] Ryerson Index (Historical Residents & Deaths)', 'url': 'https://www.ryersonindex.org/', 'description': '8.5M+ indexed notices from Australian newspapers for locating past residents', 'domain': 'ryersonindex.org'}
    ]
}

def clean_and_inject_aus_tools():
    with open('data/osint_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    columns = data.get('columns', [])
    
    total_added_aus = 0

    for col in columns:
        for w in col.get('widgets', []):
            title = w.get('title', '').strip()
            links = w.get('links', [])
            
            # Find matching Australian tools for this widget
            aus_links_to_add = []
            
            # Direct match or partial match
            for cat_key, aus_tools in AUS_CATEGORY_MAP.items():
                if cat_key == title or cat_key in title or title in cat_key:
                    aus_links_to_add.extend(aus_tools)
            
            if aus_links_to_add:
                # Deduplicate existing links by URL
                existing_urls = {l.get('url', '').lower().rstrip('/') for l in links}
                new_aus_items = []
                
                for tool in aus_links_to_add:
                    tool_url = tool['url'].lower().rstrip('/')
                    if tool_url not in existing_urls:
                        domain = clean_domain(tool['url'])
                        favicon = f"https://f.start.me/{domain}"
                        new_aus_items.append({
                            'id': int(tool.get('id') or (abs(hash(tool['url'])) % 100000000)),
                            'title': tool['title'],
                            'url': tool['url'],
                            'description': tool.get('description', ''),
                            'domain': domain,
                            'favicon': favicon,
                            'status': 200
                        })
                        existing_urls.add(tool_url)
                        total_added_aus += 1
                
                # Filter out any existing links that might be Australian and re-order:
                # All [AUS] tools AT THE TOP, followed by non-AUS tools underneath!
                all_current_links = new_aus_items + links
                
                aus_top = []
                other_bottom = []
                seen_urls = set()
                
                for l in all_current_links:
                    u = l.get('url', '').lower().rstrip('/')
                    if u in seen_urls:
                        continue
                    seen_urls.add(u)
                    
                    # If Australian link (contains [AUS], .gov.au, .com.au, .edu.au, .org.au)
                    is_aus = (
                        '[AUS]' in l.get('title', '') or 
                        '.gov.au' in l.get('url', '') or 
                        '.com.au' in l.get('url', '') or 
                        '.edu.au' in l.get('url', '') or 
                        '.org.au' in l.get('url', '') or 
                        '.net.au' in l.get('url', '') or
                        '.auda.org.au' in l.get('url', '')
                    )
                    
                    if is_aus:
                        # Ensure [AUS] tag is in title for consistency
                        if not l.get('title', '').startswith('[AUS]'):
                            l['title'] = f"[AUS] {l.get('title', '')}"
                        aus_top.append(l)
                    else:
                        other_bottom.append(l)
                
                # Set links ordered: Australian at the top, US/International underneath
                w['links'] = aus_top + other_bottom
                w['link_count'] = len(w['links'])

    # Recalculate totals
    total_widgets = sum(len(col.get('widgets', [])) for col in columns)
    total_links = sum(sum(len(w.get('links', [])) for w in col.get('widgets', [])) for col in columns)
    
    data['total_widgets'] = total_widgets
    data['total_links'] = total_links

    # Save to JSON and JS bundle
    with open('data/osint_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    with open('data/osint_data.js', 'w', encoding='utf-8') as f:
        f.write("window.BUBBSY_DATA = " + json.dumps(data, indent=2) + ";\n")

    print(f"Successfully processed all categories with Australian tools at the top!")
    print(f"Total Widgets: {total_widgets}")
    print(f"Total Links across all categories: {total_links} (Added {total_added_aus} new Australian tools)")

if __name__ == '__main__':
    clean_and_inject_aus_tools()
