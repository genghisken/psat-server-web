// 2026-02-05 KWS Javascript call to AladinLite.
// * coords - an array of sets of coordinates. From the object page only one 
//            set of coordinates is in the list. For the new quickview pages
//            there will be one set of coordinates per object displayed.
//
// * sherlock - an array of Sherlock coordinates plus descriptions.

(function () {

var localaladindivname = aladindivname;
var localobjectcoords = jsaladinglobal[localaladindivname].coords
var localobjectcoordsdeg = jsaladinglobal[localaladindivname].coordsdeg
var localobjectname = jsaladinglobal[localaladindivname].name
var localsherlock = jsaladinglobal[localaladindivname].sherlock
var localfov = jsaladinglobal[localaladindivname].fov

// 2026-11-17 KWS/Claude Emergency fix for CDS outage.
var MIRROR_DSS2_COLOR = "https://stpubdata.s3.us-east-1.amazonaws.com/mast/skybackgrounds/DSSColor";
var MIRROR_PANSTARRS_GRI = "https://stpubdata.s3.us-east-1.amazonaws.com/mast/skybackgrounds/PanSTARRS";

var SURVEYS = [
     // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
     {
        "id": "P/PanSTARRS/DR1/color-i-r-g",
        "url": MIRROR_PANSTARRS_GRI,
        "name": "PanSTARRS DR1 color i-r-g (MAST mirror)",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/Finkbeiner",
        "url": "https://skies.esac.esa.int/FinkbeinerHa",  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
        "maxOrder": 3,
        "frame": "galactic",
        "format": "jpeg fits",
        "name": "Halpha"
     },
     {
        "id": "P/Skymapper-color-IRG",
        "url": "https://skymapper.anu.edu.au/CDS_P_skymapper-color",  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
        "name": "Skymapper color (red-I,green-R,blue-G)",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/SPITZER/color",
        "url": "https://casda.csiro.au/hips/SpitzerI1I2I4color",  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
        "name": "IRAC color I1,I2,I4 - (GLIMPSE, SAGE, SAGE-SMC, SINGS)",
        "maxOrder": 9,
        "frame": "galactic",
        "format": "jpeg"
     }
  ];

A.init.then(() => {

  const status = document.getElementById('status');

  // ------------------------------------------------------------
  // Create viewer with DSS2 as base (last resort)
  // ------------------------------------------------------------
  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
  const dss2Hips = A.imageHiPS(MIRROR_DSS2_COLOR, {
    name: 'DSS2 color (MAST mirror)',
    maxOrder: 9,
    cooFrame: 'equatorial',
    imgFormat: 'jpeg'
  });
  const panstarrsHips = A.imageHiPS(MIRROR_PANSTARRS_GRI, {
    name: 'PanSTARRS DR1 color i-r-g (MAST mirror)',
    maxOrder: 11,
    cooFrame: 'equatorial',
    imgFormat: 'jpeg'
  });

  const aladin = A.aladin(localaladindivname, {
    survey: dss2Hips,  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
    fov: localfov,
    target: localobjectcoords[0] + " " + localobjectcoords[1],
    showReticle: false,
    reticleSize: 40,
    showProjectionControl: false,
    showShareControl: false,
    hipsList: [],  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
    log: false  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.
  });
  aladin.setBaseImageLayer(dss2Hips);  // 2026-11-17 KWS/Claude Emergency fix for CDS outage.

  // Add the transient label.
  var cat = A.catalog({
    name: 'Transient',
    sourceSize: 10,
    color: 'red'
  });

  aladin.addCatalog(cat, { shape: 'square' });

  // create marker with 'name' property (this will be used for the label)
  cat.addSources([
    A.marker(
      localobjectcoordsdeg[0],
      localobjectcoordsdeg[1],
      {
        popupTitle: localobjectname
      })
  ]);

  // Now add the Sherlock labels
  var contextcat = A.catalog({
    name: 'Catalogue Sources',
    sourceSize: 10,
    color: 'blue'
  });

  aladin.addCatalog(contextcat, { shape: 'square' });

  const sherlockSources = localsherlock.map(item =>
    A.marker(
      item.marker[0],   // RA (deg)
      item.marker[1],   // Dec (deg)
      {
        popupTitle: item.popupTitle,
        name: item.name   // label text (used by labelColumn)
      }
    )
  );

  contextcat.addSources(sherlockSources);

  // Add Custom HIPS cat if it's not already available
  // 2026-11-17 KWS/Claude Emergency fix for CDS outage - PS1 HiPS catalogue (CDS) removed

  // **************************************

  // Add the surveys to the drop-down menu.
  SURVEYS.forEach(s => {

    const myHips = aladin.createImageSurvey(
      s.id,        // HiPS id
      s.name,      // label shown in the dropdown
      s.url,       // base HiPS URL
      s.frame,     // 'equatorial' or 'galactic'
      s.maxOrder,  // max HiPS order
      {
        // imgFormat expects *one* format → pick the first if multiple are listed
        imgFormat: s.format.split(' ')[0]
      }
    );

    // add to the Aladin GUI (survey dropdown)
    aladin.addHiPSToFavorites(myHips);
  });



  // ------------------------------------------------------------
  // Add overlays (LOW priority first, HIGH priority last = on top)
  // ------------------------------------------------------------

  // Quick hack - because Pan-STARRS gets in the way of other layers below -30.5 degrees dec
  if (localobjectcoordsdeg[1] > -30.5){
    aladin.setOverlayImageLayer(panstarrsHips, 'panstarrs');  // 2026-11-17 KWS/Claude Emergency fix for CDS outage
  }
  // 2026-11-17 KWS/Claude Emergency fix for CDS outagei - DESI and DECaPS overlays (CDS) removed

  // ------------------------------------------------------------
  // Helpers
  // ------------------------------------------------------------

  function readPixelPromise(overlay, ra, dec) {
    return new Promise(resolve => {
      try {
        overlay.readPixel(ra, dec, p => resolve(p));
      } catch {
        resolve(null);
      }
    });
  }

  // Show overlay (like clicking the eye), probe a 3x3 grid around center
  async function showAndProbe(localId, tries = 10, delayMs = 300) {
    const ov = aladin.getOverlayImageLayer(localId);
    if (!ov) return false;

    // Same behavior as GUI
    if (typeof ov.show === 'function') ov.show();

    const offsets = [
      [0, 0],
      [0.02, 0], [-0.02, 0],
      [0, 0.02], [0, -0.02],
      [0.02, 0.02], [-0.02, -0.02],
      [0.02, -0.02], [-0.02, 0.02]
    ];

    const [ra0, dec0] = aladin.getRaDec();

    for (let t = 0; t < tries; t++) {
      for (const [dra, ddec] of offsets) {
        const px = await readPixelPromise(ov, ra0 + dra, dec0 + ddec);
        if (px && px.length && isFinite(px[0])) {
          console.log(`✔ ${localId} visible`, ov.props);
          return true;
        }
      }
      await new Promise(r => setTimeout(r, delayMs));
    }

    // No pixel → hide again
    if (typeof ov.hide === 'function') ov.hide();
    return false;
  }

  function priorityList(dec) {
    return ['panstarrs'];  // 2026-11-17 KWS/Claude Emergency fix for CDS outage
  }

  // ------------------------------------------------------------
  // Main evaluation logic
  // ------------------------------------------------------------
  async function evaluate() {
    const [ra, dec] = aladin.getRaDec();
    const order = priorityList(dec);

    status.textContent =
      `Checking surveys at RA=${ra.toFixed(3)}°, Dec=${dec.toFixed(3)}°`;

    let winner = null;

    for (const id of order) {
      if (await showAndProbe(id)) {
        winner = id;
        break;
      }
    }

    // Hide non-winners
    ['panstarrs'].forEach(id => {  // 2026-11-17 KWS/Claude Emergency fix for CDS outage
      if (id === winner) return;
      const ov = aladin.getOverlayImageLayer(id);
      if (ov && typeof ov.hide === 'function') ov.hide();
    });

    status.textContent = winner
      ? `Showing ${winner.toUpperCase()}`
      : `No overlay coverage — showing DSS2`;

    console.log('Winner:', winner || 'DSS2');
  }

  // ------------------------------------------------------------
  // Wire events (debounced)
  // ------------------------------------------------------------
  let timer = null;
  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(evaluate, 180);
  }

  setTimeout(evaluate, 800);
  aladin.on('positionChanged', schedule);
  aladin.on('zoomChanged', schedule);

  // Expose for manual testing
  window.evaluate = evaluate;
});

})();
