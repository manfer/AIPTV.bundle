<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:p="http://xspf.org/ns/0/">

<xsl:output method="xml" encoding="utf-8" indent="yes" version="1.0" />

<xsl:param name="dir">
  <xsl:text>ascending</xsl:text>
</xsl:param>

<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()" />
  </xsl:copy>
</xsl:template>

<xsl:template match="//p:trackList">
  <xsl:copy>
    <xsl:apply-templates select="@*" />
    <xsl:apply-templates select="p:track">
      <xsl:sort select="p:title" data-type="text" order='{$dir}' />
    </xsl:apply-templates>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>
