import os
import img2pdf
from PyPDF2 import PdfFileMerger


def convert(image_list, filename):
    with open(filename, "wb") as f:
        f.write(img2pdf.convert(*image_list))


def merge(old_workbook, new_photos, filename):
    if old_workbook is not None:
        with open(old_workbook, 'rb') as orig, open(new_photos, 'rb') as new:
            pdf = PdfFileMerger()
            pdf.append(orig)
            pdf.append(new)
            pdf.write(filename)
    else:
        os.rename(new_photos, filename)


def save_file(bot, file_id, full_name):
    file_to_save = bot.get_file(file_id)
    file_extension = os.path.splitext(file_to_save.file_path)[1]
    filename = full_name + file_extension.lower()
    with open(filename, "wb") as new_file:
        new_file.write(bot.download_file(file_to_save.file_path))
    return filename


def save_files(bot, file_ids, path, idx):
    for f_id in file_ids:
        idx += 1
        save_file(bot, f_id, path + "/" + str(idx))
    file_ids.clear()
    return idx
