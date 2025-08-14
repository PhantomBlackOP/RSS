<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:media="http://search.yahoo.com/mrss/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <xsl:output method="html" indent="yes" doctype-public="" doctype-system=""/>

  <xsl:template match="/">
    <html>
      <head>
        <title>Trevorion Weekly RSS Feed</title>
        <style>
          body { font-family: sans-serif; line-height: 1.6; padding: 20px; background: #f8f8f8; color: #222; }
          h1 { color: #000; }
          .item { margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid #ccc; }
          .title { font-size: 1.2em; font-weight: bold; }
          .link { color: navy; text-decoration: none; }
          .date { color: #444; font-size: 0.9em; }
          .description a { color: navy; text-decoration: none; }
          img { max-width: 640px; height: auto; }
          .heart { max-width: 640px; height: auto; }
          .content { margin-top: 10px; }
        </style>
      </head>
      <body>
        <h1>📰 Trevorion Weekly RSS Feed</h1>

        <xsl:for-each select="rss/channel/item">
          <div class="item">
            <div class="title">
              <a>
                <xsl:attribute name="class">link</xsl:attribute>
                <xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute>
                <xsl:value-of select="title"/>
              </a>
            </div>

            <div class="date">
              <xsl:value-of select="pubDate"/>
            </div>

            <xsl:if test="media:content/@url">
              <div style="margin:10px 0;">
                <img>
                  <xsl:attribute name="src"><xsl:value-of select="media:content/@url"/></xsl:attribute>
                  <xsl:attribute name="alt">Post image</xsl:attribute>
                </img>
              </div>
            </xsl:if>

            <div class="description">
              <xsl:value-of select="description" disable-output-escaping="yes"/>
            </div>

            <xsl:for-each select="content:encoded">
              <div class="content">
                <xsl:value-of select="." disable-output-escaping="yes"/>
              </div>
            </xsl:for-each>
          </div>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
