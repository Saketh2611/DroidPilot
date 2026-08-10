from droidpilot.device.uiautomator import parse_hierarchy_xml


def test_parse_hierarchy_xml():
    xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <hierarchy rotation="0">
      <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.android.chrome" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0,1080,2400]">
        <node index="1" text="Google" resource-id="com.android.chrome:id/url_bar" class="android.widget.EditText" package="com.android.chrome" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="true" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[60,200,1020,300]" />
      </node>
    </hierarchy>
    """

    nodes = parse_hierarchy_xml(xml)
    assert nodes[0]["resource_id"] == "com.android.chrome:id/url_bar"
    assert nodes[0]["text"] == "Google"
    assert nodes[0]["bounds"] == (60, 200, 1020, 300)


def test_parse_hierarchy_xml_with_nested_android_bounds():
    xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <hierarchy rotation="0">
      <node index="1" text="Chrome" resource-id="" class="android.widget.TextView" package="com.android.launcher3" content-desc="Chrome" clickable="true" bounds="[200,300][400,420]" />
    </hierarchy>
    """

    nodes = parse_hierarchy_xml(xml)
    assert nodes[0]["bounds"] == (200, 300, 400, 420)
