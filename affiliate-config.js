/* Columbus Living Well affiliate link map.
   Paste each approved tracking URL into "url". While a value is empty, the
   visible link stays on the partner's public page (no tracking, no commission).
   Only add a URL after the program has approved this site. */
window.CLW_AFFILIATES = {
  lemonade:   { network: "FlexOffers or Impact", url: "" },
  att:        { network: "FlexOffers", url: "" },
  spectrum:   { network: "FlexOffers", url: "" },
  amazon:     { network: "Amazon Associates", tag: "" },  /* e.g. yourtag-20 */
  self:       { network: "FlexOffers", url: "" },
  boom:       { network: "Boom direct", url: "" },
  cubesmart:  { network: "FlexOffers", url: "" },
  budget:     { network: "Partnerize", url: "" }
};
(function () {
  var m = window.CLW_AFFILIATES;
  document.querySelectorAll("a[data-affiliate]").forEach(function (a) {
    var c = m[a.getAttribute("data-affiliate")];
    if (!c) return;
    if (c.url) { a.href = c.url; }
    else if (c.tag) {
      try { var u = new URL(a.href); u.searchParams.set("tag", c.tag); a.href = u.toString(); } catch (e) {}
    }
  });
})();
