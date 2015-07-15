<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:p="http://xspf.org/ns/0/">
  
<xsl:output method="xml" encoding="utf-8" indent="yes" version="1.0" />

<xsl:param name="iseed" select="123" />

<xsl:template match="@*|node()">
    <xsl:copy>
        <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
</xsl:template>

<xsl:template match="//p:trackList">
  <xsl:copy>
    <xsl:apply-templates select="@*" />
    <xsl:call-template name="pick-random-item">
      <xsl:with-param name="tracks" select="p:track" />
    </xsl:call-template>
  </xsl:copy>
</xsl:template>

<xsl:template name="pick-random-item">
  <xsl:param name="tracks" />
  <xsl:param name="seed" select="$iseed" />
  <xsl:if test="$tracks">
    <!-- generate a random number using the "linear congruential generator" algorithm -->
    <xsl:variable name="a" select="1664525" />
    <xsl:variable name="c" select="1013904223" />
    <xsl:variable name="m" select="4294967296" />
    <xsl:variable name="random" select="($a * $seed + $c) mod $m" />
    <!-- scale random to integer 1..n -->
    <xsl:variable name="i" select="floor($random div $m * count($tracks)) + 1" />
    <!-- write out the corresponding item -->
    <xsl:copy-of select="$tracks[$i]" />
    <!-- recursive call with the remaining items -->
    <xsl:call-template name="pick-random-item">
      <xsl:with-param name="tracks" select="$tracks[position()!=$i]" />
      <xsl:with-param name="seed" select="$random" />
    </xsl:call-template>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>
