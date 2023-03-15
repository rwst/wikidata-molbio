// Requires wikibase-cli >= v15.16.0

module.exports = {

  template: async (id) => {
    return {
      id,
        claims: {
            P279: {
                value: "Q3333419",
                references: [
                    { P248: "Q2134522", P854: "https://plantreactome.gramene.org/PathwayBrowser/#/R-OSA-2744345&DTAB=MT" }
                ]
            }
        }
    }
  }
}
