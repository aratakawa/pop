{
    if( size(`ls "bake_root"`) == 0 )
    {
        string $locator[] = `spaceLocator -n "bake_root"`;
        print( $locator );

        // create dummy mesh, make it small
        string $bake_indirect[] = `polyCube -n "indirect_dummy"`;
        string $bake_shadow[] = `polyCube -n "shadow_dummy"`;
        xform -s 0 0 0 $bake_shadow[0];
        xform -s 0 0 0 $bake_indirect[0];

        // create shader nodes, assign them
        string $indirect_shader = `shadingNode -n "bake_indirect" -asShader mzBakePtc`;
        string $shadow_shader = `shadingNode -n "bake_shadow" -asShader mzBakePtc`;
        select -r $bake_indirect[0];
        hyperShade -assign $indirect_shader;
        select -r $bake_shadow[0];
        hyperShade -assign $shadow_shader;
        setAttr ($indirect_shader+".minThreshold") 0.001;
        setAttr -type "string" ($shadow_shader+".attribute") "";
        setAttr ($shadow_shader+".minThreshold") 0.001;

        // parent under root
        parent $bake_indirect[0] $locator[0];
        parent $bake_shadow[0] $locator[0];

        // addAttr and setAttr to options node
        string $opt = "defaultArnoldRenderOptions";
        if( !`attributeQuery -n $opt -ex "mtoa_bake_indirect"`)
            addAttr -dt "string" -ln "mtoa_bake_indirect" $opt;
        if( !`attributeQuery -n $opt -ex "mtoa_bake_shadow"`)
            addAttr -dt "string" -ln "mtoa_bake_shadow" $opt;
        setAttr -type "string" ($opt+".mtoa_bake_indirect")  ($indirect_shader+".outColor");
        setAttr -type "string" ($opt+".mtoa_bake_shadow")  ($shadow_shader+".outColor");
    }
    else
    {
        warning "bake_root already exists";
    }
}

##########################################################################

