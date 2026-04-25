MAP_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Copernicus Flood Risk Map</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    * { box-sizing: border-box; }
    html, body { height: 100%; margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #17202a; }
    body { background: #eef2f4; }
    #map { position: fixed; inset: 0; z-index: 1; }
    .panel {
      position: fixed;
      z-index: 2;
      top: 16px;
      left: 16px;
      width: min(380px, calc(100vw - 32px));
      max-height: calc(100vh - 32px);
      overflow: auto;
      background: rgba(255,255,255,0.96);
      border: 1px solid rgba(23,32,42,0.14);
      border-radius: 8px;
      box-shadow: 0 18px 45px rgba(23,32,42,0.20);
      padding: 16px;
    }
    h1 { font-size: 18px; line-height: 1.25; margin: 0 0 14px; font-weight: 700; }
    form { display: grid; gap: 12px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    label { display: grid; gap: 5px; font-size: 12px; font-weight: 650; color: #334155; }
    input {
      width: 100%;
      min-height: 38px;
      border: 1px solid #c8d1d8;
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      background: #fff;
      color: #17202a;
    }
    input[type="range"] { padding: 0; }
    input[type="checkbox"] { width: 16px; min-height: 16px; padding: 0; accent-color: #1f4f66; }
    .check-row { display: flex; align-items: center; gap: 8px; }
    button {
      min-height: 40px;
      border: 1px solid #1f4f66;
      border-radius: 6px;
      background: #1f4f66;
      color: #fff;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }
    button:disabled { opacity: 0.62; cursor: wait; }
    .status, .result {
      margin-top: 12px;
      border-top: 1px solid #dde4ea;
      padding-top: 12px;
      font-size: 13px;
      line-height: 1.45;
    }
    .result dl { display: grid; grid-template-columns: 130px 1fr; gap: 6px 10px; margin: 0; }
    .result dt { color: #51606d; }
    .result dd { margin: 0; font-weight: 650; overflow-wrap: anywhere; }
    .legend { display: grid; gap: 7px; margin-top: 12px; font-size: 12px; color: #334155; }
    .legend-row { display: flex; align-items: center; gap: 8px; }
    .swatch { width: 18px; height: 12px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.18); }
    .high { background: rgba(235, 31, 31, 0.82); }
    .medium { background: rgba(255, 158, 26, 0.68); }
    .low { background: rgba(26, 122, 245, 0.42); }
    .admin-region-label {
      color: #111827;
      background: rgba(255,255,255,0.88);
      border: 1px solid rgba(17,24,39,0.26);
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(17,24,39,0.18);
      font-size: 12px;
      font-weight: 750;
      line-height: 1.25;
      padding: 4px 6px;
      white-space: nowrap;
    }
    @media (max-width: 640px) {
      .panel { top: 8px; left: 8px; width: calc(100vw - 16px); max-height: 48vh; padding: 12px; }
      h1 { font-size: 16px; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div id="map"></div>
  <section class="panel" aria-label="Flood map controls">
    <h1>Copernicus Flood Risk Map</h1>
    <form id="controls">
      <div class="grid">
        <label>Latitude<input id="latitude" name="latitude" type="number" step="0.000001" min="-90" max="90" value="45.45" required></label>
        <label>Longitude<input id="longitude" name="longitude" type="number" step="0.000001" min="-180" max="180" value="28.05" required></label>
      </div>
      <div class="grid">
        <label>Radius meters<input id="radius" name="radius" type="number" step="100" min="100" max="100000" value="1000" required></label>
        <label>Lookback days<input id="lookback" name="lookback" type="number" step="1" min="1" max="180" value="30" required></label>
      </div>
      <div class="grid">
        <label>VV threshold dB<input id="threshold" name="threshold" type="number" step="0.5" min="-30" max="-5" value="-17" required></label>
        <label>Overlay opacity<input id="opacity" name="opacity" type="range" min="0.1" max="1" step="0.05" value="0.72"></label>
      </div>
      <label class="check-row"><input id="adminToggle" name="adminToggle" type="checkbox" checked> Show administrative borders</label>
      <button id="run" type="submit">Update map</button>
    </form>
    <div class="legend" aria-label="Heatmap legend">
      <div class="legend-row"><span class="swatch high"></span><span>High water-like SAR signal</span></div>
      <div class="legend-row"><span class="swatch medium"></span><span>Medium water-like SAR signal</span></div>
      <div class="legend-row"><span class="swatch low"></span><span>Low water-like SAR signal</span></div>
    </div>
    <div id="status" class="status">Ready</div>
    <div id="result" class="result" hidden></div>
  </section>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const metersPerDegreeLat = 111320;
    const map = L.map("map", { zoomControl: true }).setView([45.45, 28.05], 13);
    map.createPane("heatmapPane");
    map.getPane("heatmapPane").style.zIndex = 450;
    map.createPane("adminPane");
    map.getPane("adminPane").style.zIndex = 650;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);
    const adminLabelLayer = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png", {
      pane: "adminPane",
      maxZoom: 20,
      subdomains: "abcd",
      attribution: "&copy; CARTO"
    }).addTo(map);

    let marker = L.marker([45.45, 28.05]).addTo(map);
    let circle = L.circle([45.45, 28.05], { radius: 1000, color: "#1f4f66", weight: 2, fillOpacity: 0.04 }).addTo(map);
    let overlay = null;
    const adminLayer = L.geoJSON(null, {
      pane: "adminPane",
      pointToLayer: (feature, latlng) => L.marker(latlng, {
        pane: "adminPane",
        interactive: false,
        icon: L.divIcon({
          className: "admin-region-label",
          html: feature.properties.name,
          iconSize: null
        })
      }),
      style: feature => {
        if (feature.properties.kind === "admin_label") return { opacity: 0 };
        const level = Number(feature.properties.admin_level);
        if (level === 2) return { color: "#111827", weight: 2.6, opacity: 0.95 };
        if (level <= 5) return { color: "#374151", weight: 1.8, opacity: 0.88, dashArray: "6 4" };
        return { color: "#4b5563", weight: 1.2, opacity: 0.78, dashArray: "3 4" };
      },
      onEachFeature: (feature, layer) => {
        const name = feature.properties.name;
        const level = feature.properties.admin_level;
        if (name) layer.bindTooltip(`${name} · admin ${level}`, { sticky: true });
      }
    }).addTo(map);

    const form = document.getElementById("controls");
    const statusEl = document.getElementById("status");
    const resultEl = document.getElementById("result");
    const opacityEl = document.getElementById("opacity");
    const adminToggleEl = document.getElementById("adminToggle");

    function bboxFor(lat, lon, radiusMeters) {
      const latDelta = radiusMeters / metersPerDegreeLat;
      const lonDelta = radiusMeters / (metersPerDegreeLat * Math.max(Math.cos(lat * Math.PI / 180), 0.01));
      return {
        west: Math.max(-180, lon - lonDelta),
        south: Math.max(-90, lat - latDelta),
        east: Math.min(180, lon + lonDelta),
        north: Math.min(90, lat + latDelta)
      };
    }

    function values() {
      return {
        lat: Number(document.getElementById("latitude").value),
        lon: Number(document.getElementById("longitude").value),
        radius: Number(document.getElementById("radius").value),
        lookback: Number(document.getElementById("lookback").value),
        threshold: Number(document.getElementById("threshold").value),
        opacity: Number(opacityEl.value)
      };
    }

    function setBusy(isBusy) {
      document.getElementById("run").disabled = isBusy;
    }

    function renderResult(data) {
      resultEl.hidden = false;
      resultEl.innerHTML = `
        <dl>
          <dt>Status</dt><dd>${data.status}</dd>
          <dt>Flooded</dt><dd>${data.flooded}</dd>
          <dt>Confidence</dt><dd>${data.confidence}</dd>
          <dt>Water fraction</dt><dd>${Number(data.current.water_fraction).toFixed(4)}</dd>
          <dt>Water area</dt><dd>${Math.round(data.current.estimated_water_area_m2).toLocaleString()} m2</dd>
          <dt>Scene</dt><dd>${data.latest_scene.datetime}</dd>
        </dl>`;
    }

    async function updateAdminBoundaries(bbox) {
      adminLayer.clearLayers();
      if (!adminToggleEl.checked) return;
      const params = new URLSearchParams({
        west: String(bbox.west),
        south: String(bbox.south),
        east: String(bbox.east),
        north: String(bbox.north),
        admin_levels: "2,4,5,6"
      });
      const response = await fetch(`/v1/admin/boundaries?${params.toString()}`);
      if (!response.ok) return;
      adminLayer.addData(await response.json());
    }

    async function updateMap(event) {
      if (event) event.preventDefault();
      const v = values();
      const bbox = bboxFor(v.lat, v.lon, v.radius);
      const bounds = [[bbox.south, bbox.west], [bbox.north, bbox.east]];
      const params = new URLSearchParams({
        latitude: String(v.lat),
        longitude: String(v.lon),
        radius_meters: String(v.radius),
        lookback_days: String(v.lookback),
        water_threshold_db: String(v.threshold),
        width: "768",
        height: "768",
        cache_bust: String(Date.now())
      });

      setBusy(true);
      statusEl.textContent = "Loading latest Sentinel-1 scene";
      try {
        marker.setLatLng([v.lat, v.lon]);
        circle.setLatLng([v.lat, v.lon]).setRadius(v.radius);
        map.fitBounds(bounds, { padding: [32, 32] });

        const detectResponse = await fetch("/v1/flood/detect", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            area: { center: { latitude: v.lat, longitude: v.lon, radius_meters: v.radius } },
            lookback_days: v.lookback,
            water_threshold_db: v.threshold
          })
        });
        const detectData = await detectResponse.json();
        if (!detectResponse.ok) throw new Error(detectData.detail?.message || "Detection request failed");
        renderResult(detectData);

        const imageUrl = `/v1/flood/heatmap.png?${params.toString()}`;
        if (overlay) overlay.remove();
        overlay = L.imageOverlay(imageUrl, bounds, { pane: "heatmapPane", opacity: v.opacity, interactive: false }).addTo(map);
        await updateAdminBoundaries(bbox);
        statusEl.textContent = "Heatmap updated";
      } catch (error) {
        statusEl.textContent = error.message;
      } finally {
        setBusy(false);
      }
    }

    opacityEl.addEventListener("input", () => {
      if (overlay) overlay.setOpacity(Number(opacityEl.value));
    });
    adminToggleEl.addEventListener("change", () => {
      if (adminToggleEl.checked) {
        map.addLayer(adminLabelLayer);
        const v = values();
        updateAdminBoundaries(bboxFor(v.lat, v.lon, v.radius));
      } else {
        adminLayer.clearLayers();
        map.removeLayer(adminLabelLayer);
      }
    });
    form.addEventListener("submit", updateMap);
    updateMap();
  </script>
</body>
</html>
"""
