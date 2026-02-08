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
var localtransientvo = jsaladinglobal[localaladindivname].transientvo
var localsherlockvo = jsaladinglobal[localaladindivname].sherlockvo

var SURVEYS = [
     {
        "id": "P/DECaLS/DR5/color",
        "url": "http://alasky.u-strasbg.fr/DECaLS/DR5/color",
        "name": "DECaLS DR5 color",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/DES-DR1/ColorIRG",
        "url": "http://alasky.u-strasbg.fr/DES/CDS_P_DES-DR1_ColorIRG",
        "name": "DES-DR1 color (I-R-G bands)",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/DESI-Legacy-Surveys/DR10/color",
        "url": "https://alasky.cds.unistra.fr/DESI-legacy-surveys/DR10/CDS_P_DESI-Legacy-Surveys_DR10_color",
        "name": "DESI Legacy Surveys color (g, r, i, z)",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/Finkbeiner",
        "url": "http://alasky.u-strasbg.fr/FinkbeinerHalpha",
        "maxOrder": 3,
        "frame": "galactic",
        "format": "jpeg fits",
        "name": "Halpha"
     },
     {
        "id": "P/PanSTARRS/DR1/color-z-zg-g",
        "url": "http://alasky.u-strasbg.fr/Pan-STARRS/DR1/color-z-zg-g",
        "name": "PanSTARRS DR1 color z-zg-g",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/PanSTARRS/DR1/r",
        "url": "http://alasky.u-strasbg.fr/Pan-STARRS/DR1/r",
        "name": "PanSTARRS DR1 r",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/PanSTARRS/DR1/i",
        "url": "http://alasky.u-strasbg.fr/Pan-STARRS/DR1/i",
        "name": "PanSTARRS DR1 i",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/PanSTARRS/DR1/z",
        "url": "http://alasky.u-strasbg.fr/Pan-STARRS/DR1/z",
        "name": "PanSTARRS DR1 z",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/PanSTARRS/DR1/y",
        "url": "http://alasky.u-strasbg.fr/Pan-STARRS/DR1/y",
        "name": "PanSTARRS DR1 y",
        "maxOrder": 11,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/Skymapper-color-IRG",
        "url": "http://alasky.u-strasbg.fr/Skymapper/skymapper_color",
        "name": "Skymapper color (red-I,green-R,blue-G)",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/Skymapper-U",
        "url": "http://alasky.u-strasbg.fr/Skymapper/skymapper_U",
        "name": "Skymapper U-band",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/Skymapper-V",
        "url": "http://alasky.u-strasbg.fr/Skymapper/skymapper_V",
        "name": "Skymapper V-band",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/Skymapper-G",
        "url": "http://alasky.u-strasbg.fr/Skymapper/skymapper_G",
        "name": "Skymapper G-band",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/Skymapper-R",
        "url": "http://alasky.u-strasbg.fr/Skymapper/skymapper_R",
        "name": "Skymapper R-band",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/Skymapper-I",
        "url": "http://alasky.u-strasbg.fr/Skymapper/skymapper_I",
        "name": "Skymapper I-band",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/Skymapper-Z",
        "url": "http://alasky.u-strasbg.fr/Skymapper/skymapper_Z",
        "name": "Skymapper Z-band",
        "maxOrder": 9,
        "frame": "equatorial",
        "format": "png"
     },
     {
        "id": "P/HSC/DR2/wide/color-i-r-g",
        "url": "http://alasky.u-strasbg.fr/HSC/DR2/CDS_P_HSC_DR2_wide_color-i-r-g",
        "name": "HSC DR2 wide color i-r-g",
        "maxOrder": 12,
        "frame": "equatorial",
        "format": "jpeg"
     },
     {
        "id": "P/SPITZER/color",
        "url": "http://alasky.u-strasbg.fr/SpitzerI1I2I4color",
        "name": "IRAC color I1,I2,I4 - (GLIMPSE, SAGE, SAGE-SMC, SINGS)",
        "maxOrder": 9,
        "frame": "galactic",
        "format": "jpeg"
     },
     {
        "id": "P/XMM/EPIC",
        "url": "http://saada.u-strasbg.fr/xmmallsky",
        "name": "XMM-Newton stacked EPIC images (no phot. normalization)",
        "maxOrder": 7,
        "frame": "equatorial",
        "format": "png fits"
     },
     {
         "id": "P/XMM/PN/color",
          "url": "http://saada.unistra.fr/xmmpnsky",
          "name": "XMM PN colored",
          "maxOrder": 7,
          "frame": "equatorial",
          "format": "png jpeg"
     }
  ];

A.init.then(() => {

  const status = document.getElementById('status');

  // ------------------------------------------------------------
  // Create viewer with DSS2 as base (last resort)
  // ------------------------------------------------------------

  const aladin = A.aladin(localaladindivname, {
    survey: 'P/DSS2/color',
    fov: 0.1033,
    target: localobjectcoordsdeg[0] + " " + localobjectcoordsdeg[1],
    showReticle: false,
    reticleSize: 40,
    showProjectionControl: false,
    showShareControl: false
  });
  aladin.setBaseImageLayer('P/DSS2/color');

  // *** Add the sherlock crossmatches (if the exist) as a VO table ***
  if (localsherlockvo !== null){

    const sherlockBlob = new Blob([localsherlockvo], { type: 'text/xml' });
    const sherlockBlobUrl = URL.createObjectURL(sherlockBlob);
    const options = {
      name: 'Sherlock',
      color: '#0000ff',
      sourceSize: 10,
      useMarkerShape: false,  // we will draw hollow rects
      showTable: true,
      selectable: true,
      onClick: 'showTable'    // <-- critical: clicking will open/highlight the table row
    };
    
    // catalogFromURL will fetch/parse the VOTable and create a Catalog object
    const scatalog = A.catalogFromURL(sherlockBlobUrl, options);
  
    // Give it a custom hollow shape (stroke only)
    scatalog.shape = function (src, ctx) {
      if (typeof src.x !== 'number' || typeof src.y !== 'number') return;
      const size = (this.options && this.options.sourceSize) || 20;
      const half = Math.round(size / 2);
      const x = Math.round(src.x);
      const y = Math.round(src.y);
      ctx.save();
      ctx.lineWidth = 1;
      ctx.strokeStyle = this.options.color || '#00ffff';
      ctx.strokeRect(x - half, y - half, half * 2, half * 2);
      ctx.restore();
    };
  
    // Add catalog to the viewer
    aladin.addCatalog(scatalog);
  }
  // **************************************

  // *** Add the transient as a VO table ***
  const transientBlob = new Blob([localtransientvo], { type: 'text/xml' });
  const transientBlobUrl = URL.createObjectURL(transientBlob);
  const options = {
    name: 'Transient',
    color: '#ff0000',
    sourceSize: 14,
    useMarkerShape: false,  // we will draw hollow rects
    showTable: true,
    selectable: true,
    onClick: 'showTable'    // <-- critical: clicking will open/highlight the table row
  };

  // catalogFromURL will fetch/parse the VOTable and create a Catalog object
  const catalog = A.catalogFromURL(transientBlobUrl, options);

  // Give it a custom hollow shape (stroke only)
  catalog.shape = function (src, ctx) {
    if (typeof src.x !== 'number' || typeof src.y !== 'number') return;
    const size = (this.options && this.options.sourceSize) || 20;
    const half = Math.round(size / 2);
    const x = Math.round(src.x);
    const y = Math.round(src.y);
    ctx.save();
    ctx.lineWidth = 1;
    ctx.strokeStyle = this.options.color || '#00ffff';
    ctx.strokeRect(x - half, y - half, half * 2, half * 2);
    ctx.restore();
  };

  // Add catalog to the viewer
  aladin.addCatalog(catalog);

  // **************************************
  // Add Custom HIPS cat if it's not already available
  var hipsCats = {
    'ps1': A.catalogHiPS('https://axel.u-strasbg.fr/HiPSCatService/II/349/ps1', {name: 'PanSTARRS DR1 sources', shape: 'circle', sourceSize: 8, color: '#6baed6', onClick: 'showTable', name: 'PanSTARRS DR1'})
  };
  hipsCats['ps1'].hide();
  aladin.addCatalog(hipsCats['ps1']);

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
  aladin.setOverlayImageLayer('CDS/P/PanSTARRS/DR1/color', 'panstarrs');
  aladin.setOverlayImageLayer('CDS/P/DESI-Legacy-Surveys/DR10/color', 'desi');
  aladin.setOverlayImageLayer('CDS/P/DECaPS/DR2/color', 'decaps');

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
    return dec >= -31
      ? ['panstarrs', 'desi', 'decaps']
      : ['desi', 'decaps', 'panstarrs'];
  }

  // ------------------------------------------------------------
  // Main evaluation logic
  // ------------------------------------------------------------
  async function evaluate() {
    const [ra, dec] = aladin.getRaDec();
    const order = priorityList(dec);

    status.textContent = `Checking surveys at RA=${ra.toFixed(3)}°, Dec=${dec.toFixed(3)}°`;

    let winner = null;

    for (const id of order) {
      if (await showAndProbe(id)) {
        winner = id;
        break;
      }
    }

    // Hide non-winners
    ['panstarrs', 'desi', 'decaps'].forEach(id => {
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
