<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:media="http://search.yahoo.com/mrss/">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <title><xsl:value-of select="/rss/channel/title"/> – RSS</title>
        <style>
          body { font-family: system-ui, Arial, sans-serif; margin: 2rem; line-height: 1.55; }
          .item { display: grid; grid-template-columns: 160px 1fr; gap: 1rem; padding: 1rem 0; border-top: 1px solid #ddd; }
          .item:first-of-type { border-top: none; }
          img { max-width: 160px; height: auto; border-radius: 8px; }
          h2 { margin: 0 0 .25rem 0; font-size: 1.1rem; }
          .meta { color: #666; font-size: .9rem; }
        </style>
      </head>
      <body>
        <h1><xsl:value-of select="/rss/channel/title"/></h1>
        <xsl:for-each select="/rss/channel/item">
          <div class="item">
            <div>
              <xsl:if test="media:thumbnail/@url">
                <img>
                  <xsl:attribute name="src"><xsl:value-of select="media:thumbnail/@url"/></xsl:attribute>
                  <xsl:attribute name="alt"><xsl:value-of select="title"/></xsl:attribute>
                </img>
              </xsl:if>
            </div>
            <div>
              <h2><a><xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute><xsl:value-of select="title"/></a></h2>
              <div class="meta"><xsl:value-of select="pubDate"/></div>
              <div><xsl:value-of select="description"/></div>
            </div>
          </div>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
