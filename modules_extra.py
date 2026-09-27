"""Extra Bubbsy modules: additional [AUS] Australian-first intelligence lists plus
global fallback lists, and the Australian-first priority pass applied at build time.

Everything here is merged in by build_data.py. IDs are reserved so the rebuild pass
in build_data.py can strip and regenerate them idempotently.
"""


def _lk(title, url, description, domain):
    return {
        'title': title,
        'url': url,
        'description': description,
        'domain': domain,
        'favicon': 'https://f.start.me/' + domain
    }


AUS_EXTRA_WIDGETS = [
    {
        'id': 9113,
        'title': '[AUS] CYBER SECURITY, SCAMS & FRAUD',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'shield',
        'color': '#f43f5e',
        'links': [
            _lk('ACSC / cyber.gov.au', 'https://www.cyber.gov.au/', 'Australian Signals Directorate cyber advisories, alerts, and hardening guidance', 'cyber.gov.au'),
            _lk('ReportCyber (Cybercrime Reporting)', 'https://www.cyber.gov.au/report-and-recover/report', 'Official Australian portal to report cybercrime, fraud, and online incidents', 'cyber.gov.au'),
            _lk('ACSC Alerts & Advisories', 'https://www.cyber.gov.au/about-us/view-all-content/alerts-and-advisories', 'Current critical vulnerability and active exploitation alerts for Australia', 'cyber.gov.au'),
            _lk('Scamwatch (ACCC)', 'https://www.scamwatch.gov.au/', 'Live Australian scam alerts, reported scam statistics, and phishing trends', 'scamwatch.gov.au'),
            _lk('National Anti-Scam Centre', 'https://www.nasc.gov.au/', 'Cross-agency Australian scam disruption intelligence and reporting hub', 'nasc.gov.au'),
            _lk('IDCARE (Identity Theft Support)', 'https://www.idcare.org/', 'National identity and cyber support service for Australia and New Zealand', 'idcare.org'),
            _lk('OAIC Notifiable Data Breaches', 'https://www.oaic.gov.au/privacy/notifiable-data-breaches', 'Statutory Australian data breach notifications and half-yearly breach reports', 'oaic.gov.au'),
            _lk('eSafety Commissioner', 'https://www.esafety.gov.au/', 'Australian online harm reporting, image-based abuse and platform takedown requests', 'esafety.gov.au'),
            _lk('ACMA Enforcement & Registers', 'https://www.acma.gov.au/', 'Australian communications regulator: spam, telco, and broadcast enforcement actions', 'acma.gov.au'),
            _lk('AusCERT', 'https://www.auscert.org.au/', 'Australian computer emergency response team bulletins and member advisories', 'auscert.org.au'),
            _lk('AFP Cybercrime', 'https://www.afp.gov.au/crimes/cybercrime', 'Australian Federal Police cybercrime reporting, operations, and case releases', 'afp.gov.au'),
            _lk('ASD (Australian Signals Directorate)', 'https://www.asd.gov.au/', 'National threat landscape reporting and cyber security posture guidance', 'asd.gov.au'),
            _lk('ACCC Enforcement Actions', 'https://www.accc.gov.au/', 'Australian competition regulator actions, recalls, and consumer enforcement records', 'accc.gov.au'),
            _lk('Have I Been Pwned', 'https://haveibeenpwned.com/', 'Check an email address or phone number against known global breach corpora', 'haveibeenpwned.com')
        ]
    },
    {
        'id': 9114,
        'title': '[AUS] PROFESSIONAL, HEALTH & LICENCE REGISTERS',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'badge-check',
        'color': '#10b981',
        'links': [
            _lk('AHPRA Register of Practitioners', 'https://www.ahpra.gov.au/registration/registers-of-practitioners.aspx', 'Verify Australian doctors, nurses, psychologists, dentists and conditions on registration', 'ahpra.gov.au'),
            _lk('ASIC Financial Advisers Register', 'https://moneysmart.gov.au/financial-advice/financial-advisers-register', 'Licensed Australian financial advisers, employment history, and bans', 'moneysmart.gov.au'),
            _lk('ASIC Banned & Disqualified Register', 'https://asic.gov.au/online-services/search-asic-s-registers/banned-and-disqualified/', 'Australians banned from managing corporations or providing financial services', 'asic.gov.au'),
            _lk('Tax Practitioners Board Public Register', 'https://www.tpb.gov.au/public-register', 'Registered Australian tax agents, BAS agents, sanctions and terminations', 'tpb.gov.au'),
            _lk('NDIS Registered Provider Finder', 'https://www.ndis.gov.au/participants/working-providers/find-registered-provider', 'Search registered NDIS providers, registration groups, and service areas', 'ndis.gov.au'),
            _lk('NSW Fair Trading Public Register', 'https://www.onegov.nsw.gov.au/publicregister/', 'NSW trade licences, builders, electricians, motor dealers and disciplinary action', 'onegov.nsw.gov.au'),
            _lk('QBCC Licence Search (QLD)', 'https://www.qbcc.qld.gov.au/online-services/licence-search', 'Queensland building and construction licensees, defect history, and directions', 'qbcc.qld.gov.au'),
            _lk('VBA Practitioner Search (VIC)', 'https://www.vba.vic.gov.au/tools/practitioner-search', 'Victorian registered builders, plumbers, and disciplinary records', 'vba.vic.gov.au'),
            _lk('WA Online Licence Search (DEMIRS)', 'https://ols.demirs.wa.gov.au/', 'Western Australian builders, plumbers, electricians and other occupational licensees', 'demirs.wa.gov.au'),
            _lk('NT Licensing Public Register', 'https://licensingnt.nt.gov.au/PublicRegister/', 'Northern Territory occupational licence holders, including expired-within-12-months status', 'licensingnt.nt.gov.au'),
            _lk('Law Society of NSW - Find a Lawyer', 'https://www.lawsociety.com.au/for-the-public/find-a-lawyer', 'Practising NSW solicitors, firms, and practising certificate status', 'lawsociety.com.au'),
            _lk('Victorian Legal Services Board Register', 'https://lsbc.vic.gov.au/lawyer-search', 'Victorian lawyer register, conditions, and disciplinary history', 'lsbc.vic.gov.au'),
            _lk('Fair Work Ombudsman', 'https://www.fairwork.gov.au/', 'Australian workplace enforcement outcomes, court penalties, and awards', 'fairwork.gov.au'),
            _lk('Safe Work Australia', 'https://www.safeworkaustralia.gov.au/', 'National WHS statistics, prosecutions, and incident notification data', 'safeworkaustralia.gov.au'),
            _lk('Australian Immunisation Register', 'https://www.servicesaustralia.gov.au/australian-immunisation-register', 'Individual immunisation history statements via Medicare and myGov', 'servicesaustralia.gov.au')
        ]
    },
    {
        'id': 9115,
        'title': '[AUS] MAPS, GEOSPATIAL & ENVIRONMENT',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'map',
        'color': '#06b6d4',
        'links': [
            _lk('Digital Atlas of Australia', 'https://digital.atlas.gov.au/', 'National authoritative geospatial layers: boundaries, demography, infrastructure', 'digital.atlas.gov.au'),
            _lk('NationalMap', 'https://nationalmap.gov.au/', 'Federal open spatial data viewer with satellite, cadastre and thematic overlays', 'nationalmap.gov.au'),
            _lk('Geoscience Australia', 'https://www.ga.gov.au/', 'Topography, geology, earthquakes, bathymetry and national elevation datasets', 'ga.gov.au'),
            _lk('SIX Maps (NSW)', 'https://maps.six.nsw.gov.au/', 'NSW cadastral parcels, lot/DP, imagery timeline, and property boundaries', 'six.nsw.gov.au'),
            _lk('MapshareVic (VIC)', 'https://mapshare.vic.gov.au/', 'Victorian cadastre, planning overlays, aerial imagery, and public land data', 'mapshare.vic.gov.au'),
            _lk('Queensland Globe', 'https://qldglobe.information.qld.gov.au/', 'Queensland property, tenure, imagery, mining and environmental layers', 'information.qld.gov.au'),
            _lk('Landgate Map Viewer (WA)', 'https://maps.landgate.wa.gov.au/', 'Western Australian land titles, cadastre and aerial imagery viewer', 'landgate.wa.gov.au'),
            _lk('LocationSA Map Viewer (SA)', 'https://location.sa.gov.au/viewer/', 'South Australian cadastre, addressing, imagery and administrative boundaries', 'location.sa.gov.au'),
            _lk('ELVIS Elevation & Depth', 'https://elevation.fsdf.org.au/', 'Download Australian LiDAR, DEM and bathymetry tiles for terrain analysis', 'elevation.fsdf.org.au'),
            _lk('Atlas of Living Australia', 'https://www.ala.org.au/', 'Georeferenced Australian species occurrence records and survey datasets', 'ala.org.au'),
            _lk('BOM Water Information', 'http://www.bom.gov.au/water/', 'Australian river gauges, storage levels, groundwater and water accounts', 'bom.gov.au'),
            _lk('National Pollutant Inventory', 'https://www.dcceew.gov.au/environment/protection/npi', 'Facility-level Australian emissions and pollutant transfer reporting', 'dcceew.gov.au'),
            _lk('NSW Air Quality Monitoring', 'https://www.airquality.nsw.gov.au/', 'Live NSW air quality station readings, smoke and hazard reduction data', 'airquality.nsw.gov.au'),
            _lk('Sentinel Hub EO Browser', 'https://apps.sentinel-hub.com/eo-browser/', 'Free multispectral satellite imagery browser with historical comparison', 'sentinel-hub.com'),
            _lk('NASA FIRMS Fire Map', 'https://firms.modaps.eosdis.nasa.gov/map/', 'Near real-time global and Australian active fire and thermal anomaly detections', 'nasa.gov')
        ]
    },
    {
        'id': 9116,
        'title': '[AUS] BANKING, TAX, FINANCE & CONSUMER',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'banknote',
        'color': '#f59e0b',
        'links': [
            _lk('Reserve Bank of Australia', 'https://www.rba.gov.au/', 'Australian cash rate decisions, statistical tables, and payments system data', 'rba.gov.au'),
            _lk('APRA Register of Institutions', 'https://www.apra.gov.au/register-of-authorised-deposit-taking-institutions', 'Authorised Australian banks, credit unions, insurers, and superannuation funds', 'apra.gov.au'),
            _lk('AUSTRAC', 'https://www.austrac.gov.au/', 'Australian AML/CTF regulator: reporting entities, enforcement, typology reports', 'austrac.gov.au'),
            _lk('Australian Taxation Office', 'https://www.ato.gov.au/', 'ABN/GST status, corporate tax transparency reports, and lost super search', 'ato.gov.au'),
            _lk('MoneySmart Investor Alert List', 'https://moneysmart.gov.au/investment-warnings/investor-alert-list', 'ASIC list of unlicensed entities and suspected investment scam operators', 'moneysmart.gov.au'),
            _lk('BSB Number Lookup (AusPayNet)', 'https://bsb.auspaynet.com.au/', 'Resolve an Australian BSB to its issuing bank, branch and location', 'auspaynet.com.au'),
            _lk('AFCA (Financial Complaints Authority)', 'https://www.afca.org.au/', 'Australian financial firm complaint determinations and published decisions', 'afca.org.au'),
            _lk('ASIC Registers Portal', 'https://asic.gov.au/online-services/search-asic-s-registers/', 'Central entry point to all ASIC company, licence, and enforcement registers', 'asic.gov.au'),
            _lk('Australian Treasury', 'https://treasury.gov.au/', 'Budget papers, consultation submissions, and economic policy documents', 'treasury.gov.au'),
            _lk('Product Safety Australia Recalls', 'https://www.productsafety.gov.au/recalls', 'Official Australian product recall notices and supplier contact details', 'productsafety.gov.au'),
            _lk('CHOICE', 'https://www.choice.com.au/', 'Independent Australian consumer testing, recalls, and company investigations', 'choice.com.au'),
            _lk('ProductReview.com.au', 'https://www.productreview.com.au/', 'Australian consumer reviews of businesses, tradies, insurers and retailers', 'productreview.com.au'),
            _lk('ACNC Charity Financial Reports', 'https://www.acnc.gov.au/charity/charities', 'Annual information statements and financials for Australian charities', 'acnc.gov.au')
        ]
    },
    {
        'id': 9117,
        'title': '[AUS] JOBS, EDUCATION & SKILLS',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'graduation-cap',
        'color': '#8b5cf6',
        'links': [
            _lk('SEEK', 'https://www.seek.com.au/', 'Largest Australian job board - employer footprints, salary bands, role history', 'seek.com.au'),
            _lk('APSJobs (Australian Public Service)', 'https://www.apsjobs.gov.au/', 'Commonwealth government vacancies, agency structures, and classifications', 'apsjobs.gov.au'),
            _lk('Workforce Australia', 'https://www.workforceaustralia.gov.au/', 'Federal employment services portal and national vacancy listings', 'workforceaustralia.gov.au'),
            _lk('Jora Australia', 'https://au.jora.com/', 'Aggregated Australian job listings across employer sites and agencies', 'jora.com'),
            _lk('training.gov.au', 'https://training.gov.au/', 'National register of RTOs, accredited courses, and training package units', 'training.gov.au'),
            _lk('USI Registry (Unique Student Identifier)', 'https://www.usi.gov.au/', 'Verify Australian VET transcripts and student identifiers', 'usi.gov.au'),
            _lk('TEQSA National Register', 'https://www.teqsa.gov.au/students/national-register', 'Registered Australian higher education providers and course accreditation', 'teqsa.gov.au'),
            _lk('My School (ACARA)', 'https://www.myschool.edu.au/', 'Profile, funding, NAPLAN and enrolment data for every Australian school', 'myschool.edu.au'),
            _lk('ComparEd (QILT Graduate Outcomes)', 'https://www.compared.edu.au/', 'Australian graduate outcomes, employment rates and student experience data', 'compared.edu.au'),
            _lk('Jobs and Skills Australia', 'https://www.jobsandskills.gov.au/', 'Occupation profiles, labour market projections and skills shortage lists', 'jobsandskills.gov.au'),
            _lk('Universities Admissions Centre (UAC)', 'https://www.uac.edu.au/', 'NSW/ACT tertiary admissions, ATAR cutoffs and course offerings', 'uac.edu.au'),
            _lk('Australian Apprenticeships', 'https://www.australianapprenticeships.gov.au/', 'Apprenticeship pathways, incentives and registered support network', 'australianapprenticeships.gov.au'),
            _lk('Study Australia', 'https://www.studyaustralia.gov.au/', 'Official international student portal: providers, visas, and course search', 'studyaustralia.gov.au')
        ]
    },
    {
        'id': 9118,
        'title': '[AUS] AVIATION, RAIL & VESSEL TRACKING',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'plane',
        'color': '#38bdf8',
        'links': [
            _lk('CASA Australian Aircraft Register', 'https://www.casa.gov.au/search-centre/aircraft-register', 'Look up VH- registered aircraft, owners, operators and airworthiness', 'casa.gov.au'),
            _lk('Airservices Australia', 'https://www.airservicesaustralia.com/', 'Australian airspace, NOTAMs, aeronautical charts and noise complaint data', 'airservicesaustralia.com'),
            _lk('ATSB Transport Investigations', 'https://www.atsb.gov.au/', 'Australian aviation, rail and marine accident investigation reports', 'atsb.gov.au'),
            _lk('AMSA (Maritime Safety Authority)', 'https://www.amsa.gov.au/', 'Australian vessel registration, incident reporting and search & rescue', 'amsa.gov.au'),
            _lk('AMSA Port State Control Detentions', 'https://www.amsa.gov.au/vessels-operators/port-state-control', 'Port state control inspections and detained vessels in Australian ports', 'amsa.gov.au'),
            _lk('AMSA Vessel Registration', 'https://www.amsa.gov.au/vessels-operators/vessel-registration', 'Domestic commercial vessel identifiers and certificate lookups', 'amsa.gov.au'),
            _lk('ARTC Rail Network', 'https://www.artc.com.au/', 'Australian Rail Track Corporation network maps, closures and train paths', 'artc.com.au'),
            _lk('BITRE Transport Statistics', 'https://www.bitre.gov.au/statistics', 'Australian aviation route volumes, freight, road and rail statistics', 'bitre.gov.au'),
            _lk('Flightradar24', 'https://www.flightradar24.com/', 'Live global ADS-B flight tracking with playback and aircraft history', 'flightradar24.com'),
            _lk('ADS-B Exchange', 'https://globe.adsbexchange.com/', 'Unfiltered ADS-B feed including military and blocked aircraft', 'adsbexchange.com'),
            _lk('OpenSky Network', 'https://opensky-network.org/', 'Research-grade historical ADS-B data and REST API for flight analysis', 'opensky-network.org'),
            _lk('MarineTraffic', 'https://www.marinetraffic.com/', 'Global AIS vessel tracking, port calls, and ship particulars', 'marinetraffic.com'),
            _lk('VesselFinder', 'https://www.vesselfinder.com/', 'Live AIS positions, vessel photos and voyage history', 'vesselfinder.com')
        ]
    },
    {
        'id': 9119,
        'title': '[AUS] MARKETPLACES, FORUMS & COMMUNITY',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'shopping-bag',
        'color': '#ec4899',
        'links': [
            _lk('Gumtree Australia', 'https://www.gumtree.com.au/', 'Australian classifieds - seller profiles, listing history and location pivots', 'gumtree.com.au'),
            _lk('OzBargain', 'https://www.ozbargain.com.au/', 'Australian deals community with long-lived, searchable user post history', 'ozbargain.com.au'),
            _lk('Whirlpool Forums', 'https://forums.whirlpool.net.au/', 'Australian broadband and tech forum - deep archives of user activity', 'whirlpool.net.au'),
            _lk('Overclockers Australia', 'https://forums.overclockers.com.au/', 'Long-running Australian tech community with public member profiles', 'overclockers.com.au'),
            _lk('Carsales', 'https://www.carsales.com.au/', 'Australian vehicle listings, dealer footprints and price history', 'carsales.com.au'),
            _lk('Bikesales', 'https://www.bikesales.com.au/', 'Australian motorcycle marketplace and seller listings', 'bikesales.com.au'),
            _lk('Boatsales', 'https://www.boatsales.com.au/', 'Australian boat and marine listings with vendor details', 'boatsales.com.au'),
            _lk('Machines4u', 'https://machines4u.com.au/', 'Australian industrial, farm and construction machinery marketplace', 'machines4u.com.au'),
            _lk('Pickles Auctions', 'https://www.pickles.com.au/', 'Australian salvage, fleet and government asset auction records', 'pickles.com.au'),
            _lk('eBay Australia', 'https://www.ebay.com.au/', 'Australian eBay storefronts, feedback history and seller locations', 'ebay.com.au'),
            _lk('Grays', 'https://www.grays.com/', 'Australian industrial and insolvency asset auctions', 'grays.com'),
            _lk('Airtasker', 'https://www.airtasker.com/', 'Australian gig marketplace - worker profiles, reviews and locations', 'airtasker.com'),
            _lk('r/australia (Reddit)', 'https://www.reddit.com/r/australia/', 'Primary Australian subreddit for local events and community chatter', 'reddit.com'),
            _lk('Facebook Marketplace', 'https://www.facebook.com/marketplace/', 'Localised peer-to-peer listings tied to real identity profiles', 'facebook.com')
        ]
    },
    {
        'id': 9120,
        'title': '[AUS] ENERGY, UTILITIES & INFRASTRUCTURE',
        'type': 'urllist',
        'group': 'aus_intel',
        'icon': 'zap',
        'color': '#eab308',
        'links': [
            _lk('AEMO (Energy Market Operator)', 'https://aemo.com.au/', 'Live Australian NEM demand, generation, price and gas market data', 'aemo.com.au'),
            _lk('OpenNEM', 'https://opennem.org.au/', 'Open dashboard of Australian electricity generation by fuel and region', 'opennem.org.au'),
            _lk('Energy Made Easy (AER)', 'https://www.energymadeeasy.gov.au/', 'Official Australian retail energy plan and price comparison register', 'energymadeeasy.gov.au'),
            _lk('Australian Energy Regulator', 'https://www.aer.gov.au/', 'Network determinations, retailer compliance and enforcement actions', 'aer.gov.au'),
            _lk('nbn Address Check', 'https://www.nbnco.com.au/connect-home-or-business/check-your-address', 'Confirm nbn technology type, rollout status and service class at an address', 'nbnco.com.au'),
            _lk('National Broadband Map', 'https://www.infrastructure.gov.au/media-technology-communications/internet/national-broadband-map', 'Broadband availability, technology and speeds across Australian regions', 'infrastructure.gov.au'),
            _lk('ACMA Register of Radiocommunications Licences', 'https://web.acma.gov.au/rrl/register_search.main_page', 'Search Australian spectrum licences, callsigns, licensees and transmitters', 'acma.gov.au'),
            _lk('ACMA Transmitter Site Lookup', 'https://web.acma.gov.au/rrl/site_search.site_lookup', 'Geolocate Australian radio transmitter sites and licensed equipment', 'acma.gov.au'),
            _lk('Before You Dig Australia', 'https://www.byda.com.au/', 'National buried utility and asset plan enquiry service', 'byda.com.au'),
            _lk('Ausgrid Outages (NSW)', 'https://www.ausgrid.com.au/outages', 'Live NSW electricity outage map, causes and restoration estimates', 'ausgrid.com.au'),
            _lk('Energex Outage Finder (QLD)', 'https://www.energex.com.au/outages/outage-finder', 'Queensland power outage map with suburb-level incident detail', 'energex.com.au'),
            _lk('WaterNSW', 'https://www.waternsw.com.au/', 'NSW dam levels, river flows, water licences and allocation data', 'waternsw.com.au'),
            _lk('Infrastructure Australia', 'https://www.infrastructureaustralia.gov.au/', 'National infrastructure priority list, audits and project pipeline', 'infrastructureaustralia.gov.au')
        ]
    }
]


GLOBAL_EXTRA_WIDGETS = [
    {
        'id': 9301,
        'title': 'GLOBAL CORPORATE REGISTRIES & OWNERSHIP',
        'type': 'urllist',
        'group': 'records_legal',
        'icon': 'building',
        'color': '#0ea5e9',
        'links': [
            _lk('OpenCorporates', 'https://opencorporates.com/', 'Largest open database of companies and directors across 140+ jurisdictions', 'opencorporates.com'),
            _lk('OCCRP Aleph', 'https://aleph.occrp.org/', 'Investigative archive of leaks, registries, sanctions and court records', 'occrp.org'),
            _lk('ICIJ Offshore Leaks Database', 'https://offshoreleaks.icij.org/', 'Panama, Paradise and Pandora Papers entities, officers and addresses', 'icij.org'),
            _lk('OpenSanctions', 'https://www.opensanctions.org/', 'Consolidated global sanctions, PEP and watchlist entity search', 'opensanctions.org'),
            _lk('GLEIF LEI Search', 'https://search.gleif.org/', 'Legal Entity Identifiers and corporate parent/child ownership chains', 'gleif.org'),
            _lk('Open Ownership Register', 'https://www.openownership.org/', 'Beneficial ownership disclosures linked across jurisdictions', 'openownership.org'),
            _lk('UK Companies House', 'https://find-and-update.company-information.service.gov.uk/', 'Free UK company filings, officers, charges and accounts', 'service.gov.uk'),
            _lk('SEC EDGAR Full-Text Search', 'https://efts.sec.gov/LATEST/search-index?q=', 'Full-text search across all US securities filings and exhibits', 'sec.gov'),
            _lk('NZ Companies Office', 'https://companies-register.companiesoffice.govt.nz/', 'New Zealand company, director and shareholder register', 'companiesoffice.govt.nz'),
            _lk('LittleSis', 'https://littlesis.org/', 'Mapped relationships between powerful people, companies and boards', 'littlesis.org'),
            _lk('EU Business Registers (e-Justice)', 'https://e-justice.europa.eu/489/EN/business_registers__search_for_a_company_in_the_eu', 'Gateway to official company registers across EU member states', 'europa.eu'),
            _lk('North Data', 'https://www.northdata.com/', 'European company financials, networks and publication history', 'northdata.com')
        ]
    },
    {
        'id': 9302,
        'title': 'ARCHIVES, VERIFICATION & FACT-CHECK',
        'type': 'urllist',
        'group': 'tools_general',
        'icon': 'archive',
        'color': '#a855f7',
        'links': [
            _lk('RMIT ABC Fact Check', 'https://www.abc.net.au/news/factcheck/', 'Australian political and public claim verification by RMIT and the ABC', 'abc.net.au'),
            _lk('AAP FactCheck', 'https://www.aap.com.au/factcheck/', 'Australian Associated Press verification of viral local claims', 'aap.com.au'),
            _lk('Wayback Machine', 'https://web.archive.org/', 'Historic snapshots of web pages, including deleted or altered content', 'archive.org'),
            _lk('archive.today', 'https://archive.ph/', 'On-demand page freezing that captures JavaScript-heavy and paywalled pages', 'archive.ph'),
            _lk('Time Travel (Memento)', 'http://timetravel.mementoweb.org/', 'Query many web archives at once for a URL at a given date', 'mementoweb.org'),
            _lk('CachedView', 'https://cachedview.nl/', 'Fast lookup across Google, Wayback and other cache sources', 'cachedview.nl'),
            _lk('Bellingcat Online Investigation Toolkit', 'https://bellingcat.gitbook.io/toolkit', 'Curated open-source investigation tool directory maintained by Bellingcat', 'gitbook.io'),
            _lk('InVID / WeVerify Plugin', 'https://www.invid-project.eu/tools-and-services/invid-verification-plugin/', 'Video keyframe extraction, reverse search and metadata verification', 'invid-project.eu'),
            _lk('Forensically', 'https://29a.ch/photo-forensics/', 'Error level analysis, clone detection and noise inspection for images', '29a.ch'),
            _lk('FotoForensics', 'https://fotoforensics.com/', 'ELA and metadata forensics for detecting manipulated photographs', 'fotoforensics.com'),
            _lk('Google Fact Check Explorer', 'https://toolbox.google.com/factcheck/explorer', 'Search published fact checks from accredited global organisations', 'google.com'),
            _lk('WikiBlame', 'https://wikipedia.ramselehof.de/wikiblame.php', 'Find which Wikipedia revision introduced or removed specific text', 'ramselehof.de')
        ]
    },
    {
        'id': 9303,
        'title': 'SATELLITE, SPACE & EARTH OBSERVATION',
        'type': 'urllist',
        'group': 'geo_transport',
        'icon': 'satellite',
        'color': '#22d3ee',
        'links': [
            _lk('Geoscience Australia Sentinel Hotspots', 'https://hotspots.dea.ga.gov.au/', 'Australian near real-time bushfire hotspot detections from satellite', 'ga.gov.au'),
            _lk('Himawari Satellite Loops (BOM)', 'http://www.bom.gov.au/australia/satellite/', 'Australian Bureau of Meteorology Himawari satellite imagery loops', 'bom.gov.au'),
            _lk('Copernicus Browser', 'https://browser.dataspace.copernicus.eu/', 'Free Sentinel-1/2/3 imagery with band maths and time comparison', 'copernicus.eu'),
            _lk('NASA Worldview', 'https://worldview.earthdata.nasa.gov/', 'Daily global satellite imagery layers including fires, smoke and aerosols', 'nasa.gov'),
            _lk('USGS EarthExplorer', 'https://earthexplorer.usgs.gov/', 'Landsat, aerial and declassified satellite imagery archive back to the 1940s', 'usgs.gov'),
            _lk('Planet Explorer', 'https://www.planet.com/explorer/', 'High-cadence commercial imagery basemaps with monthly mosaics', 'planet.com'),
            _lk('Zoom Earth', 'https://zoom.earth/', 'Live weather satellite loops, cyclone tracking and wildfire overlays', 'zoom.earth'),
            _lk('Sentinel Playground', 'https://apps.sentinel-hub.com/sentinel-playground/', 'Quick multispectral index visualisation (NDVI, moisture, urban)', 'sentinel-hub.com'),
            _lk('N2YO Satellite Tracking', 'https://www.n2yo.com/', 'Live orbital positions, passes and TLE data for tracked satellites', 'n2yo.com'),
            _lk('Heavens-Above', 'https://heavens-above.com/', 'Satellite pass predictions and sky charts for any observer location', 'heavens-above.com'),
            _lk('CelesTrak', 'https://celestrak.org/', 'Authoritative TLE catalogues, conjunction data and orbital element sets', 'celestrak.org'),
            _lk('Space-Track.org', 'https://www.space-track.org/', 'Official US space catalogue with historical orbital element access', 'space-track.org')
        ]
    },
    {
        'id': 9304,
        'title': 'OPSEC, PRIVACY & SECURE COMMS',
        'type': 'urllist',
        'group': 'cyber_intel',
        'icon': 'lock',
        'color': '#94a3b8',
        'links': [
            _lk('OAIC Privacy Rights (AU)', 'https://www.oaic.gov.au/privacy/your-privacy-rights', 'Australian Privacy Principles, access requests and complaint pathways', 'oaic.gov.au'),
            _lk('Privacy Guides', 'https://www.privacyguides.org/', 'Vetted privacy tool recommendations and threat-model driven guidance', 'privacyguides.org'),
            _lk('Tor Project', 'https://www.torproject.org/', 'Anonymity network, browser downloads and bridge configuration', 'torproject.org'),
            _lk('Tails OS', 'https://tails.net/', 'Amnesic live operating system routing all traffic through Tor', 'tails.net'),
            _lk('Whonix', 'https://www.whonix.org/', 'Isolated VM architecture that prevents IP leaks during investigations', 'whonix.org'),
            _lk('Mullvad VPN', 'https://mullvad.net/', 'Account-number-only VPN with no email requirement and audited clients', 'mullvad.net'),
            _lk('Proton Mail', 'https://proton.me/mail', 'End-to-end encrypted mail with anonymous signup options', 'proton.me'),
            _lk('SimpleX Chat', 'https://simplex.chat/', 'Messenger with no persistent user identifiers or account handles', 'simplex.chat'),
            _lk('Signal', 'https://signal.org/', 'End-to-end encrypted messaging and calls with sealed sender', 'signal.org'),
            _lk('KeePassXC', 'https://keepassxc.org/', 'Offline, cross-platform password vault with no cloud dependency', 'keepassxc.org'),
            _lk('Cryptomator', 'https://cryptomator.org/', 'Client-side encryption for files stored in any cloud provider', 'cryptomator.org'),
            _lk('Exodus Privacy', 'https://reports.exodus-privacy.eu.org/', 'Analyse trackers and permissions embedded in Android applications', 'exodus-privacy.eu.org'),
            _lk("Terms of Service; Didn't Read", 'https://tosdr.org/', 'Graded summaries of platform terms, data retention and rights', 'tosdr.org')
        ]
    }
]


EXTRA_WIDGET_IDS = ({w['id'] for w in AUS_EXTRA_WIDGETS} |
                    {w['id'] for w in GLOBAL_EXTRA_WIDGETS})


# --- AUSTRALIAN-FIRST PRIORITY PASS -----------------------------------------

# Australian-operated services that do not sit on a .au domain but should still
# rank as local sources.
AU_DOMAIN_ALLOWLIST = {
    'idcare.org',
    'grays.com',
    'airtasker.com',
    'airservicesaustralia.com',
    'canstar.com.au',
}


def is_au_link(link):
    """True when a link points at an Australian domain or an explicitly AU resource."""
    domain = (link.get('domain') or '').lower()
    url = (link.get('url') or '').lower()
    if domain.endswith('.au') or '.au/' in url or url.rstrip('/').endswith('.au'):
        return True
    return domain in AU_DOMAIN_ALLOWLIST


def apply_au_priority(columns):
    """Tag every link with `au`, float Australian links to the top of each widget,
    and float [AUS] widgets to the top of each column.

    Sorts are stable, so existing curation order is preserved within each tier.
    Returns the number of links flagged as Australian.
    """
    au_total = 0
    for col in columns:
        for widget in col.get('widgets', []):
            links = widget.get('links') or []
            for link in links:
                link['au'] = is_au_link(link)
                if link['au']:
                    au_total += 1
            if links:
                widget['links'] = sorted(links, key=lambda l: 0 if l.get('au') else 1)
                widget['au_count'] = sum(1 for l in links if l.get('au'))
            widget['au_module'] = str(widget.get('title', '')).startswith('[AUS]')
        col['widgets'] = sorted(
            col.get('widgets', []),
            key=lambda w: 0 if w.get('au_module') else 1
        )
    return au_total
