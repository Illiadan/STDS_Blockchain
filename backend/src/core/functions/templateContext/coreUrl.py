from core.functions.blocks import blockQueries as fBQ


def templateContextGeneration():
    qsBlocks = fBQ.getAllBlocks().order_by("-id")
    blocks = []
    for block in qsBlocks:
        blocks.append(block.__dict__)
    context = {
        "blocks": blocks,
    }
    return context
