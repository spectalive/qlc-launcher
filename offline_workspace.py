"""Create a temporary verification copy with no physical I/O bindings."""

import xml.etree.ElementTree as ET


def offline_workspace(source, destination):
    """Keep the show but remove all engine I/O and startup function bindings."""
    tree = ET.parse(source)
    namespace = "http://www.qlcplus.org/Workspace"
    ET.register_namespace("", namespace)
    engine = tree.find(f"{{{namespace}}}Engine")
    if engine is None:
        raise RuntimeError("The workspace has no QLC+ Engine.")
    for node in list(engine):
        if node.tag.rsplit("}", 1)[-1] in {"InputOutputMap", "StartupFunction"}:
            engine.remove(node)
    # QLC+ rejects an otherwise valid XML workspace without this doctype and
    # can then restore the previous show, including its live hardware patch.
    destination.write_bytes(
        b'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Workspace>\n'
        + ET.tostring(tree.getroot(), encoding="UTF-8")
    )
    return destination
