from urllib import request
import json
import cv2
import random
import carb
import omni.kit.asset_converter
import omni.kit.commands
import omni.usd
from PIL import Image
from pathlib import Path


def get_data(url: str):
    f = request.urlopen(url)
    data_json = json.loads(f.read())
    return data_json


def get_random_frame(videofile: str):
    vidcap = cv2.VideoCapture(videofile)
    # get total number of frames
    total_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    random_frame_number = random.randint(60, total_frames)
    # set frame position
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_number)
    success, image = vidcap.read()
    if success:
        suffix = Path(videofile).suffix
        img_path = f"{videofile.split(suffix)[0]}.jpg"
        cv2.imwrite(img_path, image)
        return img_path


# Progress of processing.
def progress_callback(current_step: int, total: int):
    # Show progress
    print(f"{current_step} of {total}")


# Convert asset file(obj/fbx/glTF, etc) to usd.
async def convert_asset_to_usd(input_asset: str, output_usd: str):
    # Input options are defaults.
    converter_context = omni.kit.asset_converter.AssetConverterContext()
    converter_context.ignore_materials = False
    converter_context.ignore_camera = False
    converter_context.ignore_animations = False
    converter_context.ignore_light = False
    converter_context.export_preview_surface = False
    converter_context.use_meter_as_world_unit = False
    converter_context.create_world_as_default_root_prim = True
    converter_context.embed_textures = True
    converter_context.convert_fbx_to_y_up = False
    converter_context.convert_fbx_to_z_up = False
    converter_context.merge_all_meshes = False
    converter_context.use_double_precision_to_usd_transform_op = False
    converter_context.ignore_pivots = False
    converter_context.keep_all_materials = True
    converter_context.smooth_normals = True
    instance = omni.kit.asset_converter.get_instance()
    task = instance.create_converter_task(input_asset, output_usd, progress_callback, converter_context)

    # Wait for completion.
    success = await task.wait_until_finished()
    if not success:
        carb.log_error(task.get_status(), task.get_detailed_error())
    else:
        print("converting done")


def download_file(url: str, download_path: Path):
    request.urlretrieve(url, download_path)


def import_file_to_scene(usd_path: Path):
    stage = omni.usd.get_context().get_stage()
    if not stage:
        return

    name = usd_path.stem
    prim_path = omni.usd.get_stage_next_free_path(stage, "/" + name, True)

    omni.kit.commands.execute(
        "CreateReferenceCommand", path_to=prim_path, asset_path=str(usd_path), usd_context=omni.usd.get_context()
    )


def get_img_size(img_path: Path):
    im = Image.open(img_path)
    width, height = im.size
    return width, height


def download_motion(asset_path: Path, name: str, file_type: str = "fbx"):
    from .window import MoveaiAssetsMarketlaceWindow

    download_dir = asset_path / "anim_files" / file_type
    download_dir.mkdir(parents=True, exist_ok=True)

    download_path = download_dir / f"{name}.{file_type}"
    for motion in MoveaiAssetsMarketlaceWindow.data["motions"]:
        if name == motion["title"]:
            download_file(motion["files"][f"{file_type}_url"], download_path)
            import_file_to_scene(download_path)
            return
