<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="yes" doctype-public="" doctype-system=""/>
  <xsl:template match="/">
    <html>
    <head>
      <title>Trevorion Anime/AI RSS Feed</title>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <meta property="og:description" content="A weekly digest highlighting daily AI-generated anime art, news, comics, and articles by @Trevorion. Dive into a curated blend of creativity, culture, and commentary." />        
      <meta name="description" content="A weekly digest highlighting daily AI-generated anime art, news, comics, and articles by @Trevorion. Dive into a curated blend of creativity, culture, and commentary." />
      <meta property="og:image" content="https://pbs.twimg.com/media/GouKfB4XQAEvXW7?format=jpg&name=4096x4096" />
      <meta name="twitter:image" content="https://pbs.twimg.com/media/GouKfB4XQAEvXW7?format=jpg&name=4096x4096" />

      <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; background: #f8f8f8; color: #222; }
        h1 { color: #000; }
        .item { margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid #ccc; }
        .title { font-size: 1.2em; font-weight: bold; }
        .link { color: navy; text-decoration: none; }
        .date { color: #444; font-size: 0.9em; }
        .description a { color: navy; text-decoration: none; }
      </style>
    </head>
    <body>
        <div style="vertical-align: middle; text-align: left;">
            <a href="https://trevorion.io"><img src="/assets/Anime%20AIS.jpg" alt="Trevorion Avatar" style="width: 100px; height: 100px; float: left; margin-right:10px;" /></a>
            <div style="overflow: hidden;">
                <h1>📰 Trevorion Anime/AI RSS Feed
                  <xsl:if test="/rss/channel/lastBuildDate">
                    <br/>
                    <span style="font-weight: normal;">
                      📅 <em><xsl:value-of select="/rss/channel/lastBuildDate"/></em>
                    </span>
                  </xsl:if>
                </h1>
            </div>                
        </div>
        <div style="text-align: left; width: 640px; height: auto;">
                <hr/>
                <h3>
                  <span style="font-weight: normal;">
                    From anime-style AI art to sharp cultural insights, the Trevorion Weekly Feed delivers a handpicked blend of daily visuals, memes, tech news, and original articles. Updated every Monday, it's your portal to a vibrant intersection of art, AI, and storytelling.
                  </span>                      
                </h3>
                <h6>
                  <span style="font-weight: bold;">
                    🏷️ #AI #Anime #News #Articles #DailyImage #AnimeAI #AIArt #WeeklyDigest #Comics #Trevorion #AnimeStyle #Highlights
                  </span>
                </h6>
        </div>
    <hr/><br/>      
      <xsl:for-each select="rss/channel/item">
        <div class="item">
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
      </xsl:for-each>
    </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
