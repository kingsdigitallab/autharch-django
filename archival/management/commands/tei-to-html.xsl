<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Convert TEI into XHTML, with attributes used to express the
       original TEI elements and attributes to allow for conversion
       back into TEI. -->

  <xsl:output encoding="utf-8" indent="yes" omit-xml-declaration="yes" />

  <xsl:strip-space elements="tei:*" />
  <xsl:preserve-space elements="tei:add tei:del tei:unclear" />

  <xsl:template match="tei:add">
    <xsl:call-template name="tei-element-in-html">
      <xsl:with-param name="element" select="'ins'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tei:body">
    <xsl:call-template name="tei-element-in-html">
      <xsl:with-param name="element" select="'div'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tei:del">
    <xsl:call-template name="tei-element-in-html">
      <xsl:with-param name="element" select="'del'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tei:hi[@rend='underline']">
    <xsl:call-template name="tei-element-in-html">
      <xsl:with-param name="element" select="'u'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tei:lb">
    <xsl:call-template name="tei-element-in-html">
      <xsl:with-param name="element" select="'br'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tei:p">
    <xsl:call-template name="tei-element-in-html">
      <xsl:with-param name="element" select="'p'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tei:TEI">
    <xsl:apply-templates select="tei:text/tei:body" />
  </xsl:template>

  <xsl:template match="tei:teiHeader" />

  <xsl:template match="tei:*">
    <xsl:call-template name="tei-element-in-html" />
  </xsl:template>

  <xsl:template match="@*" />

  <xsl:template match="tei:*" mode="tei-as-attribute">
    <xsl:attribute name="class">
      <xsl:value-of select="concat('tei-', local-name())" />
      <xsl:if test="@type">
        <xsl:text> tei-type-</xsl:text>
        <xsl:value-of select="@type" />
      </xsl:if>
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="@*" mode="tei-as-attribute">
    <xsl:attribute name="{concat('data-tei-', local-name())}">
      <xsl:value-of select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template name="tei-element-in-html">
    <xsl:param name="element" select="'span'" />
    <xsl:element name="{$element}">
      <xsl:apply-templates mode="tei-as-attribute" select="." />
      <xsl:apply-templates mode="tei-as-attribute" select="@*" />
      <xsl:apply-templates select="@*" />
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
