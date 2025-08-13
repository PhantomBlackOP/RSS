<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:media="http://search.yahoo.com/mrss/">
  <xsl:output method="html" indent="yes"/>
  <xsl:template match="/">
    <html>
    <head>
      <title>Trevorion Weekly RSS Feed</title>
      <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; background: #f8f8f8; color: #222; }
        h1 { color: #000; }
        .item { display: grid; grid-template-columns: 160px 1fr; gap: 1rem; padding-bottom: 15px; margin-bottom: 30px; border-bottom: 1px solid #ccc; }
        .title { font-size: 1.2em; font-weight: bold; }
        .link { color: navy; text-decoration: none; }
        .date { color: #444; font-size: 0.9em; margin-bottom: .5em; }
        img { max-width: 160px; height: auto; border-radius: 8px; }
        .description a { color: navy; text-decoration: none; }
      </style>
    </head>
    <body>
      <h1>📰 Trevorion Weekly RSS Feed</h1>
      <xsl:for-each select="rss/channel/item">
        <div class="item">
          <div>
            <xsl:if test="media:thumbnail/@url">
              <img>
                <xsl:attribute name="src">
                  <xsl:value-of select="media:thumbnail/@url"/>
                </xsl:attribute>
                <xsl:attribute name="alt">
                  <xsl:value-of select="title"/>
                </xsl:attribute>
              </img>
            </xsl:if>
          </div>
          <div>
            <div class="title">
              <a class="link">
                <xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute>
                <xsl:value-of select="title"/>
              </a>
            </div>
            <div class="date">
              <xsl:value-of select="pubDate"/>
            </div>
            <div class="description">
              <xsl:value-of select="description" disable-output-escaping="yes"/>
            </div>
          </div>
        </div>
      </xsl:for-each>
    </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
