/* Taal en teksten van PA-WFT.nl (nl/en). Laad dit script als eerste van de eigen scripts.
   - window.PA_TAAL: 'nl' of 'en' (uit <html lang>); Nederlands is de bron en de standaard.
   - window.PA_T(sleutel, ...args): tekst in de pagina-taal. {0}, {1} in een sjabloon worden door de argumenten vervangen;
     een functie krijgt de argumenten zelf (voor meervoud).
   - window.PA_PAD, PA_SITE, PA_PAGINA(sleutel, hash), PA_URL(sleutel, hash): één plek met de pagina-URL's per taal.
   - window.PA_BASIS: absoluut pad naar de scripts (/assets/js/). */
(function(){
  var taal = document.documentElement.lang === 'en' ? 'en' : 'nl';
  var en = taal === 'en';
  window.PA_TAAL = taal;
  window.PA_BASIS = '/assets/js/';
  window.PA_LOGO = '/assets/logo/dfo-logo.png';

  // Kaart van pagina-URL's per taal (de Engelse pagina's staan in /en/)
  var PAGINAS = {
    nl: {index:'index.html', toets:'toets.html', nieuw:'nieuw.html', begrippen:'begrippen.html', pe:'pe-punten-wft.html', vragen:'vragen.html', over:'over.html', privacy:'privacy.html', voorwaarden:'gebruiksvoorwaarden.html', klachten:'klachten.html', zoeken:'zoeken.html'},
    en: {index:'index.html', toets:'quiz.html', nieuw:'whats-new.html', begrippen:'glossary.html', pe:'pe-explained.html', vragen:'faq.html', over:'about.html', privacy:'privacy.html', voorwaarden:'terms.html', klachten:'complaints.html', zoeken:'search.html'}
  };
  window.PA_PAGINAS = PAGINAS;
  window.PA_PAD = en ? '/en/' : '';                       // relatief pad naar de pagina's van deze taal
  window.PA_SITE = 'https://pa-wft.nl/' + (en ? 'en/' : ''); // volledige URL van de voorpagina van deze taal
  function bestand(sleutel){ return PAGINAS[taal][sleutel] || (sleutel.indexOf('module-') === 0 ? sleutel + '.html' : sleutel); }
  // Relatieve link naar een pagina van deze taal; sleutel: 'toets', 'index', 'zoeken', 'module-<id>', enz.
  window.PA_PAGINA = function(sleutel, hash){ return window.PA_PAD + bestand(sleutel) + (hash ? '#' + hash : ''); };
  // Volledige URL (voor mails, certificaat, agenda)
  window.PA_URL = function(sleutel, hash){ return window.PA_SITE + bestand(sleutel) + (hash ? '#' + hash : ''); };

  // sleutel: [nederlands, engels]
  var D = {
    // ---- toets.js: start
    'alleModules': ['Alle modules', 'All modules'],
    'mijnPakket': ['Mijn pakket', 'My package'],
    'mijnPakketLijst': ['Mijn pakket: {0}', 'My package: {0}'],
    'bijgewerkt1': ['Vragen van deze module laatst bijgewerkt op {0}.', 'Questions for this module were last updated on {0}.'],
    'bijgewerktN': ['{0} modules. Oudste bijwerkdatum: {1}.', '{0} modules. Oldest update date: {1}.'],
    'aantal': [
      function(n, v){ return 'Met deze keuze: ' + n + (n === 1 ? ' module, ' : ' modules, ') + v + ' vragen.'; },
      function(n, v){ return 'With this selection: ' + n + (n === 1 ? ' module, ' : ' modules, ') + v + ' questions.'; }],
    'kiesMinimaal': ['Kies minimaal één module.', 'Select at least one module.'],
    'startToets': ['Start de toets', 'Start the quiz'],
    'modules': ['Modules', 'Modules'],
    'niets': ['Niets', 'None'],
    'kiesKwal': ['Kies op beroepskwalificatie', 'Choose by professional qualification'],
    'testKennis': ['Test je kennis', 'Test your knowledge'],
    'startUitleg': ['Kies een of meer modules. Bij één module krijg je 7 willekeurige meerkeuzevragen, en voor elke module die je toevoegt 5 extra (2 modules: 12 vragen, 3 modules: 17). Na elk antwoord zie je bij alle vier de antwoorden waarom ze goed of fout zijn. Na afloop ontvang je een certificaat met je resultaat.',
      'Choose one or more modules. With one module you get 7 random multiple-choice questions, plus 5 extra for every module you add (2 modules: 12 questions, 3 modules: 17). After each answer you see why each of the four answers is right or wrong. Afterwards you receive a certificate with your result.'],
    'advies': ['Doe de toets elk kwartaal, zo blijf je permanent actueel. Bewaar het certificaat in je personeelsdossier en lever het ook in bij je werkgever.',
      'Take the quiz every quarter to stay permanently up to date. Keep the certificate in your personnel file and also hand it in to your employer.'],
    'teamKopieer': ['Kopieer de link naar deze toets voor je team', 'Copy the link to this quiz for your team'],
    'teamGekopieerd': [' Gekopieerd: {0}', ' Copied: {0}'],
    'teamZelf': [' Kopieer deze link: {0}', ' Copy this link: {0}'],
    'vragenLaden': ['Vragen laden…', 'Loading questions…'],
    'ladenMislukt': ['De vragen konden niet worden geladen. Controleer je internetverbinding en probeer het opnieuw.', 'The questions could not be loaded. Check your internet connection and try again.'],
    // ---- toets.js: vragen
    'goed': ['✓ Goed: ', '✓ Correct: '],
    'fout': ['✗ Fout: ', '✗ Wrong: '],
    'jouwAntwoord': [' (jouw antwoord)', ' (your answer)'],
    'meldOnderwerp': ['check deze vraag op PA-WFT.nl', 'please check this question on PA-WFT.nl'],
    'meldModule': ['Module: Wft {0}', 'Module: Wft {0}'],
    'meldTerm': ['Toetsterm CDFD: {0}', 'CDFD exam term: {0}'],
    'meldVraag': ['Vraag:', 'Question:'],
    'meldAntwoorden': ['Antwoorden:', 'Answers:'],
    'meldGegevenJuist': ['  [gegeven als juist]', '  [given as correct]'],
    'meldMijnAntwoord': ['  [mijn antwoord]', '  [my answer]'],
    'meldUitleg': ['Uitleg bij het juiste antwoord:', 'Explanation of the correct answer:'],
    'meldTwijfel': ['Mijn twijfel:', 'My doubt:'],
    'meldLink': ['Twijfel je over deze vraag of het antwoord? Mail hem direct naar DFO', 'Doubts about this question or its answer? Email it directly to DFO'],
    'volgende': ['Volgende vraag', 'Next question'],
    'bekijkResultaat': ['Bekijk resultaat', 'View result'],
    'oefenVraag': ['Oefenronde · vraag {0} van {1}', 'Practice round · question {0} of {1}'],
    'vraagVan': ['Vraag {0} van {1}', 'Question {0} of {1}'],
    'badgeTerm': [' · toetsterm {0}', ' · exam term {0}'],
    'voortgang': ['Voortgang', 'Progress'],
    'stoppenVraag': ['Toets stoppen? Je antwoorden gaan verloren.', 'Stop the quiz? Your answers will be lost.'],
    'stoppen': ['Stoppen', 'Stop'],
    'juistKop': ['Goed!', 'Correct!'],
    'onjuistKop': ['Helaas, dat is niet juist.', 'Unfortunately, that is not correct.'],
    // ---- toets.js: oefenronde en resultaat
    'oefenKlaarFout': ['Oefenronde klaar. Een paar vragen zijn nog lastig: lees de uitleg en oefen ze nog een keer.', 'Practice round finished. A few questions are still tricky: read the explanations and practise them once more.'],
    'oefenKlaarGoed': ['Oefenronde klaar: nu alles goed.', 'Practice round finished: everything correct now.'],
    'oefenTelt': ['Een oefenronde telt niet mee voor je certificaat.', 'A practice round does not count towards your certificate.'],
    'oefenDeze': [
      function(n){ return 'Oefen deze ' + (n === 1 ? 'vraag' : n + ' vragen') + ' nog een keer'; },
      function(n){ return 'Practise ' + (n === 1 ? 'this question' : 'these ' + n + ' questions') + ' once more'; }],
    'terugResultaat': ['Terug naar je resultaat en certificaat', 'Back to your result and certificate'],
    'nieuweToets': ['Nieuwe toets', 'New quiz'],
    'hoera': ['HOERA, gefeliciteerd!', 'HOORAY, congratulations!'],
    'oordeel1': ['Foutloos. Uitstekend!', 'Flawless. Excellent!'],
    'oordeel2': ['Goed gedaan, ruim voldoende.', 'Well done, a comfortable pass.'],
    'oordeel3': ['Redelijk, maar er is ruimte voor verbetering.', 'Fair, but there is room for improvement.'],
    'oordeel4': ['Dat kan beter. Lees de uitleg hieronder en probeer het opnieuw.', 'You can do better. Read the explanations below and try again.'],
    'oefenFoute': [
      function(f){ return 'Oefen je ' + (f === 1 ? 'foute vraag' : f + ' foute vragen') + ' opnieuw'; },
      function(f){ return 'Practise your ' + (f === 1 ? 'incorrect question' : f + ' incorrect questions') + ' again'; }],
    'nieuweZelfde': ['Nieuwe toets, zelfde module', 'New quiz, same module'],
    'andereModule': ['Andere module kiezen', 'Choose another module'],
    'printAntwoorden': ['Print beantwoorde vragen', 'Print answered questions'],
    'overzichtUitleg': ['Overzicht met uitleg', 'Overview with explanations'],
    // ---- toets.js: certificaatformulier
    'vulNaam': ['Vul je naam in.', 'Enter your name.'],
    'geldigGeb': ['Vul een geldige geboortedatum in, of laat het veld leeg.', 'Enter a valid date of birth, or leave the field empty.'],
    'geldigMail': ['Vul een geldig e-mailadres in.', 'Enter a valid email address.'],
    'geldigWerkgever': ['Vul een geldig e-mailadres van je werkgever in, of laat het veld leeg.', 'Enter a valid email address for your employer, or leave the field empty.'],
    'ontvangCert': ['Ontvang je certificaat', 'Receive your certificate'],
    'certUitleg': ['Vul je gegevens in. Ze komen op het certificaat en blijven in je eigen browser: er gaat niets naar DFO en er wordt niets bewaard. Met "Mail met pdf-bijlage" maak je het certificaat als pdf en zet je het als bijlage in een mail aan jezelf.',
      'Enter your details. They appear on the certificate and stay in your own browser: nothing is sent to DFO and nothing is stored. With "Email with pdf attachment" you create the certificate as a pdf and attach it to an email to yourself.'],
    'labelNaam': ['Naam op het certificaat', 'Name on the certificate'],
    'labelGeb': ['Geboortedatum (optioneel)', 'Date of birth (optional)'],
    'labelMail': ['Je e-mailadres', 'Your email address'],
    'labelBedrijf': ['Bedrijf waar je werkt (optioneel)', 'Company you work for (optional)'],
    'labelWerkgever': ['E-mailadres werkgever, voor een kopie (optioneel)', 'Employer email address, for a copy (optional)'],
    'mailPdf': ['Mail met pdf-bijlage', 'Email with pdf attachment'],
    'downloadPdf': ['Download pdf', 'Download pdf'],
    'pdfGedownload': ['De pdf is gedownload: {0}.', 'The pdf has been downloaded: {0}.'],
    'bekijkPrint': ['Bekijken of printen', 'View or print'],
    'mailTekstLink': ['Of mail het certificaat als tekst, zonder bijlage', 'Or email the certificate as text, without attachment'],
    'certMaken': ['Het certificaat wordt gemaakt…', 'The certificate is being created…'],
    'deelBericht': ['Aan: {0}', 'To: {0}'],
    'deelKopie': [' (kopie: {0})', ' (copy: {0})'],
    'deelKlaar': ['Kies je mail-app; de pdf zit als bijlage in het bericht. Vul zo nodig {0} in als ontvanger.', 'Choose your mail app; the pdf is attached to the message. If necessary, enter {0} as the recipient.'],
    'en': [' en ', ' and '],
    'emlKlaar': ['Er is een mailconcept gedownload: {0}. Open het bestand: Outlook en Windows Mail openen een concept aan {1}{2}, met de pdf al als bijlage. Klik op Verzenden. Opent jouw mailprogramma het niet als concept? Gebruik dan "Download pdf" en voeg de pdf zelf toe.',
      'An email draft has been downloaded: {0}. Open the file: Outlook and Windows Mail open a draft addressed to {1}{2}, with the pdf already attached. Click Send. Does your email program not open it as a draft? Then use "Download pdf" and add the pdf yourself.'],
    'emlKopie': [' met een kopie aan {0}', ' with a copy to {0}'],
    'popupAntw': ['Pop-up geblokkeerd. Sta pop-ups toe om de antwoorden te printen.', 'Pop-up blocked. Allow pop-ups to print the answers.'],
    'popupCert': ['Pop-up geblokkeerd. Sta pop-ups toe om het certificaat te openen.', 'Pop-up blocked. Allow pop-ups to open the certificate.'],
    'pdfNietGeladen': ['pdf niet geladen', 'pdf not loaded'],
    // ---- certificaat en mail
    'disclaimer': ['Eigen verklaring van de deelnemer. De deelnemer heeft de oefentoets van Wft Permanent Actueel (PA-WFT.nl), een activiteit van DFO BV (KvK 32068727), De Wel 14–16, 3871 MV Hoevelaken, zelf gemaakt en de gegevens zelf ingevuld. DFO BV heeft identiteit en resultaat niet gecontroleerd en registreert niets. Het certificaat is geen Wft-diploma, geen PE-examen en levert geen PE-punten op.',
      'Self-declaration by the participant. The participant took the practice quiz of Wft Permanent Actueel (PA-WFT.nl), an activity of DFO BV (Dutch Chamber of Commerce number 32068727), De Wel 14–16, 3871 MV Hoevelaken, the Netherlands, personally and entered the details personally. DFO BV has not verified identity or result and does not register anything. The quiz concerns Dutch laws and regulations. The certificate is not a Wft diploma, not a PE exam and does not earn PE points.'],
    'mailTitel': ['Certificaat PA-toets — Wft Permanent Actueel', 'Certificate PA quiz — Wft Permanent Actueel'],
    'mNaam': ['Naam: ', 'Name: '],
    'mGeb': ['Geboortedatum: ', 'Date of birth: '],
    'mMail': ['E-mailadres: ', 'Email address: '],
    'mBedrijf': ['Bedrijf: ', 'Company: '],
    'mVerstuurd': ['Verstuurd op: ', 'Sent on: '],
    'mResultaat': ['Resultaat: {0} van {1} goed ({2}%)', 'Result: {0} of {1} correct ({2}%)'],
    'mModule': ['Module: ', 'Module: '],
    'mModules': ['Modules: ', 'Modules: '],
    'mVragenUit': ['Vragen uit: ', 'Questions from: '],
    'mDatum': ['Datum: ', 'Date: '],
    'mBank': ['Vragenbank bijgewerkt: ', 'Question bank updated: '],
    'mNummer': ['Certificaatnummer: ', 'Certificate number: '],
    'mOpnieuw': ['Doe de toets opnieuw: ', 'Take the quiz again: '],
    'mOnderwerp': ['Certificaat PA-toets {0} — {1} ({2}/{3})', 'Certificate PA quiz {0} — {1} ({2}/{3})'],
    'pdfNaam': ['Certificaat-PA-toets-{0}.pdf', 'Certificate-PA-quiz-{0}.pdf'],
    'emlNaam': ['Mail-certificaat-PA-toets-{0}.eml', 'Email-certificate-PA-quiz-{0}.eml'],
    'cNummer': ['Certificaatnummer', 'Certificate number'],
    'cLogoAlt': ['DFO — dienstverlening voor financiële ondernemers', 'DFO — services for financial entrepreneurs'],
    'cTitel': ['Certificaat', 'Certificate'],
    'cSub': ['PA-toets · Wft Permanent Actueel', 'PA quiz · Wft Permanent Actueel'],
    'cEigenVerklaring': ['Eigen verklaring van', 'Self-declaration by'],
    'cGeb': ['Geboortedatum', 'Date of birth'],
    'cMail': ['E-mailadres', 'Email address'],
    'cBedrijf': ['Bedrijf', 'Company'],
    'cVerstuurd': ['Verstuurd op', 'Sent on'],
    'cAangemaakt': ['Aangemaakt op', 'Created on'],
    'cAfgelegd': ['de PA-toets heeft afgelegd met het volgende resultaat:', 'has taken the PA quiz with the following result:'],
    'cGoed': ['vragen goed', 'questions correct'],
    'cScore': ['score', 'score'],
    'cModule': ['module', 'module'],
    'cModulesMv': ['modules', 'modules'],
    'cBank': ['vragenbank bijgewerkt', 'question bank updated'],
    'cModulesLabel': ['Modules', 'Modules'],
    'cVragenUit': ['Vragen uit', 'Questions from'],
    'cOpnieuw': [' Doe de toets opnieuw op ', ' Take the quiz again at '],
    'cDocTitel': ['Certificaat PA-toets — {0}', 'Certificate PA quiz — {0}'],
    'stempelLabel': ['Stempel DFO BV', 'DFO BV stamp'],
    'pdfTitel': ['Certificaat PA-toets {0} — {1}', 'Certificate PA quiz {0} — {1}'],
    'pdfSubject': ['PA-toets', 'PA quiz'],
    'pdfSubtitel': ['PA-TOETS · WFT PERMANENT ACTUEEL', 'PA QUIZ · WFT PERMANENT ACTUEEL'],
    'pdfOpnieuwUrl': ['pa-wft.nl/toets.html', 'pa-wft.nl/en/quiz.html'],
    // ---- toets.js: afdruk beantwoorde vragen
    'aVraagNr': ['Vraag {0} · Wft {1}', 'Question {0} · Wft {1}'],
    'aTermCdfd': [' · toetsterm CDFD {0}', ' · CDFD exam term {0}'],
    'aGoed': ['✓ Goed', '✓ Correct'],
    'aFout': ['✗ Fout', '✗ Wrong'],
    'aJuist': [' — juist antwoord', ' — correct answer'],
    'aJouw': [' — jouw antwoord', ' — your answer'],
    'aDocTitel': ['Beantwoorde vragen PA-toets {0}', 'Answered questions PA quiz {0}'],
    'aKop': ['Beantwoorde vragen — PA-toets', 'Answered questions — PA quiz'],
    'aMeta': ['{0} · {1} van {2} goed ({3}%) · {4} · certificaatnummer {5} · ', '{0} · {1} of {2} correct ({3}%) · {4} · certificate number {5} · '],
    'aVoet': ['Wft Permanent Actueel is een activiteit van DFO BV. Oefentoets, geen PE-examen. Doe de toets opnieuw op {0}', 'Wft Permanent Actueel is an activity of DFO BV. Practice quiz, not a PE exam. The quiz concerns Dutch laws and regulations. Take the quiz again at {0}'],
    'uur': [' uur', ''],
    // ---- tip.js
    'tipOnderwerp': ['Tip: test gratis je Wft-kennis op PA-WFT.nl', 'Tip: test your Wft knowledge for free at PA-WFT.nl'],
    'tipTekst': [
      function(naam){
        return 'Hoi,\n\n'
          + 'Ik test mijn Wft-kennis op PA-WFT.nl en dacht meteen aan jou. In een paar minuten weet je hoe actueel je kennis is, en het kost niets.\n\n'
          + 'Wat je krijgt:\n'
          + '- Praktijkcasussen uit alle 9 Wft-modules, van Basis tot Pensioen. Kies één module of je hele pakket.\n'
          + '- Bij elk antwoord uitleg waarom het goed of fout is.\n'
          + '- Vragen afgestemd op de toetstermen van het CDFD per 1 april 2026.\n'
          + '- Na afloop een certificaat voor je personeelsdossier.\n'
          + '- Gratis voor alle adviseurs, zonder account en zonder abonnement.\n\n'
          + 'Doe de toets elk kwartaal, zo blijf je permanent actueel. Zullen we kijken wie de hoogste score haalt?\n\n'
          + 'Start hier: ' + window.PA_URL('toets') + '\n\n'
          + 'Groet,\n' + (naam || '') + '\n\n'
          + '--\nWft Permanent Actueel (' + window.PA_SITE + ') is een activiteit van DFO BV. Oefentoets, geen PE-examen.\n';
      },
      function(naam){
        return 'Hi,\n\n'
          + 'I am testing my Wft knowledge on PA-WFT.nl and immediately thought of you. In a few minutes you will know how up to date your knowledge is, and it costs nothing.\n\n'
          + 'What you get:\n'
          + '- Practical case studies from all 9 Wft modules, from Basic to Pensions. Choose one module or your whole package.\n'
          + '- An explanation with every answer of why it is right or wrong.\n'
          + '- Questions aligned with the CDFD exam terms as of 1 April 2026.\n'
          + '- A certificate for your personnel file afterwards.\n'
          + '- Free for all advisers, without an account and without a subscription.\n\n'
          + 'Take the quiz every quarter to stay permanently up to date. Shall we see who gets the highest score?\n\n'
          + 'Start here: ' + window.PA_URL('toets') + '\n\n'
          + 'Kind regards,\n' + (naam || '') + '\n\n'
          + '--\nWft Permanent Actueel (' + window.PA_SITE + ') is an activity of DFO BV. Practice quiz, not a PE exam. The quiz concerns Dutch laws and regulations.\n';
      }],
    'tipOnderwerpLabel': ['Onderwerp: ', 'Subject: '],
    'tipKop': ['Tip je collega’s', 'Tip your colleagues'],
    'tipUitleg': ['Ken je collega’s die hun Wft-kennis ook actueel willen houden? Vul hun e-mailadressen in. We zetten een mail met een korte uitnodiging klaar in je eigen mailprogramma; jij kijkt hem na en verstuurt hem zelf. De adressen gaan niet naar DFO en worden nergens bewaard.',
      'Do you know colleagues who also want to keep their Wft knowledge up to date? Enter their email addresses. We prepare an email with a short invitation in your own email program; you check it and send it yourself. The addresses are not sent to DFO and are not stored anywhere.'],
    'tipLabelMail': ['E-mailadressen van je collega’s', 'Email addresses of your colleagues'],
    'tipHulp': ['Eén of meer adressen, gescheiden door een komma, puntkomma of nieuwe regel.', 'One or more addresses, separated by a comma, semicolon or new line.'],
    'tipPlaceholder': ['collega@kantoor.nl, collega2@kantoor.nl', 'colleague@company.com, colleague2@company.com'],
    'tipLabelNaam': ['Je naam (onder de mail, optioneel)', 'Your name (below the email, optional)'],
    'tipBcc': [' Verstuur als bcc, zodat collega’s elkaars adres niet zien', ' Send as bcc, so colleagues cannot see each other’s address'],
    'tipKnop': ['Zet de mail klaar', 'Prepare the email'],
    'tipKopieer': ['Kopieer de tekst', 'Copy the text'],
    'tipMinimaal': ['Vul minimaal één e-mailadres in.', 'Enter at least one email address.'],
    'tipControleer': [
      function(n, lijst){ return 'Controleer ' + (n === 1 ? 'dit adres' : 'deze adressen') + ': ' + lijst; },
      function(n, lijst){ return 'Please check ' + (n === 1 ? 'this address' : 'these addresses') + ': ' + lijst; }],
    'tipMax': ['Maximaal {0} adressen per keer.', 'A maximum of {0} addresses at a time.'],
    'tipOpent': [
      function(n){ return 'Je mailprogramma opent met de uitnodiging aan ' + (n === 1 ? '1 collega' : n + ' collega’s') + '. Opent er niets, of gebruik je webmail? Kies dan "Kopieer de tekst".'; },
      function(n){ return 'Your email program opens with the invitation to ' + (n === 1 ? '1 colleague' : n + ' colleagues') + '. Does nothing open, or do you use webmail? Then choose "Copy the text".'; }],
    'tipOpKlembord': ['De tekst staat op je klembord. Plak hem in een nieuwe mail.', 'The text is on your clipboard. Paste it into a new email.'],
    'tipKopieerMislukt': ['Kopiëren lukte niet. Selecteer de tekst hieronder en kopieer hem zelf.', 'Copying failed. Select the text below and copy it yourself.'],
    'tipBekijk': ['Bekijk de tekst van de mail', 'View the text of the email'],
    // ---- agenda.js
    'agTitel': ['PA-toets Wft Permanent Actueel', 'PA quiz Wft Permanent Actueel'],
    'agTekst': ['Doe de PA-toets, zo blijf je permanent actueel. Bewaar het certificaat in je personeelsdossier en lever het in bij je werkgever. {0}',
      'Take the PA quiz to stay permanently up to date. Keep the certificate in your personnel file and hand it in to your employer. {0}'],
    'agUitleg': ['Zet een herinnering in je agenda: elk kwartaal, de komende 5 jaar, met een link naar de toets.', 'Add a reminder to your calendar: every quarter for the next 5 years, with a link to the quiz.'],
    'agIcsNaam': ['pa-toets-elk-kwartaal.ics', 'pa-quiz-every-quarter.ics'],
    'agIcsKnop': ['Zet in mijn agenda (Outlook, Apple)', 'Add to my calendar (Outlook, Apple)'],
    'agGoogle': ['Google Agenda', 'Google Calendar'],
    'agProdid': ['NL', 'EN'],
    // ---- zoek.js
    'zMinimaal': ['Typ minimaal twee letters.', 'Type at least two letters.'],
    'zResultaten': [
      function(n, q){ return n + (n === 30 ? '+ resultaten' : n === 1 ? ' resultaat' : ' resultaten') + ' voor "' + q + '".'; },
      function(n, q){ return n + (n === 30 ? '+ results' : n === 1 ? ' result' : ' results') + ' for "' + q + '".'; }],
    'zGeen': ['Geen resultaten voor "{0}". Probeer een ander of korter zoekwoord.', 'No results for "{0}". Try a different or shorter search term.'],
    'zPagina': ['Pagina', 'Page'],
    // ---- main.js
    'laatstBijgewerkt': ['Laatst bijgewerkt: {0}', 'Last updated: {0}'],
    'doeToets': ['Doe de toets →', 'Take the quiz →'],
    'kwal0': ['Adviseur Hypothecair krediet', 'Mortgage Credit Adviser'],
    'kwal1': ['Adviseur Vermogen', 'Wealth Adviser'],
    'kwal2': ['Adviseur Pensioen', 'Pensions Adviser'],
    'kwal3': ['Adviseur Consumptief krediet', 'Consumer Credit Adviser'],
    'kwal4': ['Adviseur Schadeverzekering zakelijk', 'Non-life Insurance (Commercial) Adviser'],
    'kwal5': ['Adviseur Schadeverzekering particulier', 'Non-life Insurance (Personal) Adviser'],
    'kwal6': ['Adviseur Inkomen', 'Income Adviser'],
    'kwal7': ['Adviseur Zorgverzekering', 'Health Insurance Adviser'],
    'modTeller': [
      function(n){ return n === 1 ? '1 module' : n + ' modules'; },
      function(n){ return n === 1 ? '1 module' : n + ' modules'; }],
    'kiesKwalLijst': ['Kies een of meer beroepskwalificaties', 'Select one or more professional qualifications'],
    'checkNoot': ['Van deze kwalificatie toont de check alleen de eigen module. Controleer de volledige samenstelling bij de <a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">adviesbevoegdheden van het CDFD</a>.',
      'For this qualification the check shows only its own module. Check the full composition at the <a href="https://cdfd.nl/adviseurs/" target="_blank" rel="noopener">advisory authorisations of the CDFD</a> (Dutch website).']
  };

  // PA_T(sleutel, ...args): tekst in de pagina-taal; onbekende sleutel in het Engels valt terug op Nederlands
  window.PA_T = function(sleutel){
    var e = D[sleutel];
    if(!e) return sleutel;
    var v = e[en ? 1 : 0];
    if(v === undefined) v = e[0];
    var args = [].slice.call(arguments, 1);
    if(typeof v === 'function') return v.apply(null, args);
    return v.replace(/\{(\d+)\}/g, function(m, i){ return args[+i] !== undefined ? args[+i] : m; });
  };
})();
