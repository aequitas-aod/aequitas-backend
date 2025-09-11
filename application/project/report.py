import io
import json
import os
import re
import subprocess
from io import BytesIO
from tempfile import TemporaryDirectory

import matplotlib.pyplot as plt
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    KeepTogether,
)

from utils.logs import logger

extra_feature_selection = False


def to_camel_case(s):
    s = s.strip()
    if not s:
        return ""

    # If first character is already uppercase, return as-is
    if s[0].isupper():
        return s

    # Otherwise, convert to PascalCase
    words = s.split()
    return " ".join(word.capitalize() for word in words)


# def get_custom_packets(folder):
#     packets_dict = {}
#
#     for filename in os.listdir(folder):
#         if "Custom" in filename:
#             full_path = os.path.join(folder, filename)
#             packets_dict[filename] = full_path
#
#     return packets_dict


def is_csv(value):
    try:
        pd.read_csv(io.StringIO(value))
        return True
    except Exception:
        return False


def is_json(val):
    if not isinstance(val, str):
        return False
    try:
        json.loads(val)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def dataframe_has_json_column(df: pd.DataFrame) -> bool:
    """
    Returns True if any column in the DataFrame contains at least one stringified JSON value.
    """
    for column in df.columns:
        if df[column].apply(is_json).any():
            return True
    return False


def is_json_string(string):
    try:
        json.loads(string)
        return True
    except (ValueError, TypeError):
        return False


def convert_svg_to_png(svg_path, png_path):
    subprocess.run(["rsvg-convert", "-f", "png", "-o", png_path, svg_path], check=True)


def graph_creator(temp_dir, output_folder, key, svg_value):
    output_folder = temp_dir + "/" + output_folder
    os.makedirs(output_folder, exist_ok=True)
    try:
        svg_output = os.path.join(output_folder, f"{key}.svg")
        png_output = os.path.join(output_folder, f"{key}.png")

        with open(svg_output, "w", encoding="utf-8") as f:
            f.write(svg_value)

        convert_svg_to_png(svg_output, png_output)
    except UnicodeDecodeError:
        logger.info(f"File '{svg_value}' (key: {key}) is not plain UTF-8 text.")


def add_title_overlay(page, title_text):
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0, 0, 0)

    # Measure text width and calculate centered x
    text_width = c.stringWidth(title_text, "Helvetica-Bold", 24)
    x = (width - text_width) / 2
    y = height - 36  # Adjust vertical position if needed

    c.drawString(x, y, title_text)
    c.save()
    packet.seek(0)

    overlay_reader = PdfReader(packet)
    overlay_page = overlay_reader.pages[0]
    page.merge_page(overlay_page)
    return page


def PDFCreator2(temp_dir, folder, file_name):
    # Temporary in-memory PDF to hold new pages
    first = True
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter

    title = folder

    folder: str = temp_dir + "/" + folder
    final_report_path: str = temp_dir + "/" + file_name

    # Sort images (you can add your logic to define sections here)
    images = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    images.sort(key=lambda f: os.path.getctime(os.path.join(folder, f)))

    if images:
        if first:
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width / 2, height - 30, title)
            first = False

        for img_file in images:
            img_path = os.path.join(folder, img_file)

            # Draw a title based on the file name (without extension)
            title = os.path.splitext(img_file)[0].split("__")[0].replace("_", " ")
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width * 0.2, height - 130, to_camel_case(title))

            # Draw the image
            c.drawImage(
                img_path,
                0,
                0,
                width=width,
                height=height,
                preserveAspectRatio=True,
                anchor="c",
            )

            c.showPage()

        c.save()
        packet.seek(0)
        # Read the in-memory PDF
        new_pdf = PdfReader(packet)

        # If output PDF already exists, read it and append new pages
        if os.path.exists(final_report_path):
            existing_pdf = PdfReader(final_report_path)
            writer = PdfWriter()

            for page in existing_pdf.pages:
                writer.add_page(page)

            for page in new_pdf.pages:
                writer.add_page(page)

            with open(final_report_path, "wb") as f_out:
                writer.write(f_out)
            logger.info(f"Appended to existing PDF at {final_report_path}")
        else:
            # Save as new PDF
            writer = PdfWriter()
            for page in new_pdf.pages:
                writer.add_page(page)

            with open(final_report_path, "wb") as f_out:
                writer.write(f_out)
            logger.info(f"PDF created at {final_report_path}")

    pdfs = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    pdfs.sort(key=lambda f: os.path.getctime(os.path.join(folder, f)))

    if pdfs:
        writer = PdfWriter()

        # If report.pdf already exists, add its pages first
        if os.path.exists(final_report_path):
            logger.info(f"Appending to existing {final_report_path}")
            with open(final_report_path, "rb") as existing:
                reader = PdfReader(existing)
                for page in reader.pages:
                    writer.add_page(page)

        first_pdf = True
        if not first:
            first_pdf = False

        # Add pages from other PDFs in the folder
        for pdf_file in pdfs:
            full_path = os.path.join(folder, pdf_file)
            if os.path.abspath(full_path) == os.path.abspath(final_report_path):
                continue  # skip report.pdf itself

            logger.info(f"Adding {pdf_file}")
            reader = PdfReader(full_path)

            for i, page in enumerate(reader.pages):
                # Add title overlay only on the first page of the first PDF
                if first_pdf and i == 0:
                    logger.info(f"Adding title to {pdf_file}'s first page")
                    page = add_title_overlay(page, title)

                writer.add_page(page)

            first_pdf = False  # Only first PDF gets title on first page

        # Save to output PDF
        # with open(temp_dir + "/" + output_pdf, "wb") as f_out:
        with open(final_report_path, "wb") as f_out:
            writer.write(f_out)

    logger.info(f"Report generated at {final_report_path}")


def csv_to_pdf_table(temp_dir, folder, output_pdf, csv_string):
    folder = temp_dir + "/" + folder
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 7
    styleN.leading = 9

    subtitle_style = styles["Heading2"]

    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists

    output_pdf += ".pdf"

    df = pd.read_csv(io.StringIO(csv_string))
    if dataframe_has_json_column(df):
        csv_with_json_to_pdf(folder, output_pdf, csv_string)
    else:
        # Prepare table data with wrapped cells
        data = [
            [Paragraph(str(cell), styleN) for cell in row]
            for row in [df.columns.tolist()] + df.values.tolist()
        ]

        # Column widths
        page_width, _ = landscape(letter)
        usable_width = page_width - 60  # left + right margin (30 each)
        num_columns = len(df.columns)
        col_widths = [usable_width / num_columns] * num_columns

        # Create table
        table = Table(data, colWidths=col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        # Build output path
        base_name = os.path.basename(output_pdf)
        output_path = os.path.join(folder, base_name)

        # Title
        file_title = os.path.splitext(base_name)[0].split("__")[0].replace("_", " ")
        subtitle_para = Paragraph(to_camel_case(file_title), subtitle_style)

        # Assemble PDF content
        elements = [Spacer(1, 6), subtitle_para, Spacer(1, 12), table]

        # Build PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            leftMargin=30,
            rightMargin=30,
            topMargin=30,
            bottomMargin=30,
        )
        doc.build(elements)

        logger.info(f"Created PDF: {output_path}")


def csv_with_json_to_pdf(folder, output_pdf, csv_file):
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 7
    styleN.leading = 9

    subtitle_style = styles["Heading2"]

    spacer = Spacer(1, 12)

    elements = [spacer]

    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists

    table_para_title = Paragraph(
        to_camel_case(output_pdf.split("__")[0]), subtitle_style
    )
    elements.append(table_para_title)

    count = 0
    col = []
    rows = []
    f = csv_file.splitlines()
    # with io.StringIO(csv_file) as f:
    for line in f:
        count += 1
        parts = line.strip().split(",")
        isArray = False
        isJson = False
        str_array = ""
        json_string = ""
        if count == 1:
            col = parts
        else:
            fixed_line = []
            for word in parts:
                if ("{" in word or isJson) and not isArray:
                    isJson = True
                    if "}" in word:
                        json_string += word
                        isJson = False
                        json_string_fixed = (
                            json_string.replace('""', '"')
                            .replace('"{', "{")
                            .replace('}"', "}")
                        )
                        fixed_line.append(json.loads(json_string_fixed))
                        json_string = ""
                    else:
                        json_string += word + ", "
                elif ("[" in word or isArray) and not isJson:
                    isArray = True
                    if "]" in word:
                        str_array += word
                        isArray = False
                        fixed_str_array = (
                            str_array.replace('""', '"')
                            .replace('"[', "[")
                            .replace(']"', "]")
                        )
                        array = json.loads(fixed_str_array)
                        fixed_line.append(array)
                    else:
                        str_array += word + ", "
                else:
                    fixed_line.append(word)

            rows.append(fixed_line)

    df = pd.DataFrame(rows, columns=col)

    # Prepare PDF
    pdf_path = os.path.join(folder, output_pdf)
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]

    # Prepare header
    columns = df.columns.tolist()
    table_data = [columns]

    # Constants for image size
    MAX_IMAGE_WIDTH = 100
    MAX_IMAGE_HEIGHT = 70

    # Build each row dynamically
    for _, row in df.iterrows():
        row_cells = []

        for col in df.columns:
            value = row[col]

            # Handle array/list: convert to string and truncate
            if isinstance(value, list):
                value_str = ", ".join(map(str, value))
                value_str = truncate_text(value_str)
                row_cells.append(Paragraph(value_str, styleN))

            # Handle JSON histogram
            elif isinstance(value, (dict, str)) and (
                (
                    isinstance(value, str)
                    and value.strip().startswith("{")
                    and "keys" in value
                )
                or isinstance(value, dict)
            ):
                try:
                    hist_data = json.loads(value) if isinstance(value, str) else value
                    fig, ax = plt.subplots(figsize=(2, 1.2))
                    ax.bar(hist_data["keys"], hist_data["values"])

                    # Hide x-axis tick labels and ticks, but keep the spine (line)
                    ax.set_xticks([])  # Remove tick marks
                    ax.set_xticklabels([])  # Remove tick labels
                    # Note: Do NOT hide the spine to keep the bottom line

                    plt.tight_layout()

                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format="PNG")
                    plt.close(fig)
                    img_buffer.seek(0)

                    img = Image(
                        img_buffer, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT
                    )  # image size fixed here
                    row_cells.append(img)
                except Exception:
                    row_cells.append(Paragraph("Invalid Histogram", styleN))

            # Handle long strings: truncate if needed
            elif isinstance(value, str):
                value_str = truncate_text(value)
                row_cells.append(Paragraph(value_str, styleN))

            # Other types: just convert and truncate if too long
            else:
                value_str = truncate_text(value)
                row_cells.append(Paragraph(value_str, styleN))

        table_data.append(row_cells)

    MAX_WIDTH = 150  # max width for text columns
    usable_width = landscape(letter)[0] - 60  # 30 margin on each side

    col_widths = []
    for col_name in df.columns:
        # Arrays get fixed width 80
        if df[col_name].apply(lambda x: isinstance(x, list)).any():
            col_widths.append(80)

        # Histograms (dict or JSON string) get double width
        elif (
            df[col_name]
            .apply(
                lambda x: (
                    isinstance(x, dict)
                    or (
                        isinstance(x, str) and x.strip().startswith("{") and "keys" in x
                    )
                )
            )
            .any()
        ):
            col_widths.append(1.2 * MAX_IMAGE_WIDTH)

        else:
            # Distribute remaining width evenly but max MAX_WIDTH
            col_widths.append(min(usable_width / len(df.columns), MAX_WIDTH))

    # Create and style table
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table._argW = col_widths  # reinforce widths for layout
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]
        )
    )

    elements.append(table)

    # Build PDF
    doc.build(elements)
    logger.info("PDF of a table with json generated at:", pdf_path)


def truncate_text(text, max_len=150):
    text = str(text)
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def json_to_pdf2(temp_dir, folder, section_title, json_string):
    folder = temp_dir + "/" + folder
    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists

    styles = getSampleStyleSheet()
    section_title_style = styles["Heading2"]

    pdf_filename = folder + "/" + section_title + ".pdf"

    elements = [
        Spacer(1, 24),
        Paragraph(to_camel_case(section_title.split("__")[0]), section_title_style),
        Spacer(1, 12),
    ]

    logger.info(section_title)
    data = json.loads(json_string)

    cleaned_data = {key.strip('" '): value for key, value in data.items()}

    def contains_when(data):
        if not isinstance(data, dict):
            return False
        for key, val in data.items():
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict) and "when" in item:
                        return True
        return False

    def search_key(obj, key):
        if isinstance(obj, dict):
            if key in obj:
                return True
            return any(search_key(v, key) for v in obj.values())
        elif isinstance(obj, list):
            return any(search_key(item, key) for item in obj)
        return False

    if contains_when(cleaned_data):
        histogram_json_to_pdf(folder, section_title, data)
    elif search_key(cleaned_data, "suggested_proxy"):
        suggested_json_to_pdf(folder, section_title, data)
    elif search_key(cleaned_data, "$algorithm"):
        preprocessing_json_to_pdf(folder, section_title, data)
    else:
        # Auto-infer all unique inner keys
        columns = set()
        for props in cleaned_data.values():
            columns.update(props.keys())

        # Sort columns to keep them consistent
        columns = sorted(columns)

        # Value formatting
        def format_value(val):
            if isinstance(val, bool):
                return "✔" if val else "✘"
            elif isinstance(val, float):
                return f"{val * 100:.0f}%"  # convert to percentage
            return str(val)

        # Build table rows
        table_data = [["Field Name"] + columns]  # Add headers
        for field_name, properties in cleaned_data.items():
            row = [field_name] + [format_value(properties.get(col)) for col in columns]
            table_data.append(row)

        # Create PDF
        if (
            (search_key(cleaned_data, "target"))
            and (search_key(cleaned_data, "sensitive"))
            and (search_key(cleaned_data, "drop"))
        ):
            os.makedirs(
                "ReportData/FeatureSelection", exist_ok=True
            )  # Ensure output folder exists
            pdf_filename = "ReportData/FeatureSelection/" + section_title + ".pdf"
            global extra_feature_selection
            extra_feature_selection = True
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)

        # Create and style the table
        table = Table(table_data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ]
            )
        )

        elements.append(table)
        doc.build(elements)

        logger.info(f"PDF saved as: {pdf_filename}")


def create_histogram_image(labels, values, img_path, title=None):
    plt.figure(figsize=(4, 3))
    plt.bar(labels, values, color="skyblue")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if title:
        plt.title(title, fontsize=8)
    plt.savefig(img_path)
    plt.close()


def sanitize_filename(text):
    return re.sub(r"[^\w\-_.]", "_", str(text))


def histogram_json_to_pdf(folder, pdf_name, json_value):
    os.makedirs(folder, exist_ok=True)

    pdf_path = os.path.join(folder, f"{pdf_name}.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    left_heading2 = ParagraphStyle(
        "LeftHeading2", parent=styles["Heading2"], alignment=TA_LEFT
    )
    elements.append(
        Paragraph(
            to_camel_case(pdf_name.split("__")[0].replace("_", " ")), left_heading2
        )
    )

    elements.append(Spacer(1, 24))

    with TemporaryDirectory() as tmpdir:
        for metric_name, records in json_value.items():
            if not records:
                continue

            when_keys = list(records[0].get("when", {}).keys())
            if len(when_keys) < 2:
                continue
            first_attr, second_attr = when_keys[0], when_keys[1]

            first_vals = sorted(
                set(r["when"][first_attr] for r in records if first_attr in r["when"])
            )
            second_vals = sorted(
                set(r["when"][second_attr] for r in records if second_attr in r["when"])
            )

            data_map = {
                col_val: {row_val: None for row_val in first_vals}
                for col_val in second_vals
            }

            for rec in records:
                w = rec["when"]
                val = rec.get("value", None)
                if val is None:
                    continue
                f_val = w.get(first_attr)
                s_val = w.get(second_attr)
                if f_val in first_vals and s_val in second_vals:
                    data_map[s_val][f_val] = val

            # Break second_vals into chunks of max 8 columns
            chunk_size = 6
            for i in range(0, len(second_vals), chunk_size):
                chunk = second_vals[i : i + chunk_size]

                # Create header row for this chunk
                header_row = [""] + chunk
                # Create image row for this chunk
                img_cells = []
                for col_val in chunk:
                    labels = []
                    values = []
                    for f_val in first_vals:
                        v = data_map[col_val][f_val]
                        if v is not None:
                            labels.append(str(f_val))
                            values.append(v)
                    img_path = os.path.join(
                        tmpdir, f"{metric_name}_{sanitize_filename(col_val)}.png"
                    )
                    create_histogram_image(labels, values, img_path, title=col_val)
                    img = Image(img_path, width=100, height=80)
                    img_cells.append(img)

                data_rows = [["Values"] + img_cells]

                table_data = [header_row] + data_rows

                col_widths = [100] + [110] * len(chunk)
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ]
                    )
                )

                elements.append(
                    KeepTogether(
                        [
                            Paragraph(
                                to_camel_case(metric_name.split("__")[0]),
                                styles["Heading2"],
                            ),
                            Spacer(1, 12),
                            table,
                        ]
                    )
                )
                elements.append(Spacer(1, 24))

        doc.build(elements)
        logger.info(f"PDF created at: {pdf_path}")


def suggested_json_to_pdf(folder, name, data):
    os.makedirs(folder, exist_ok=True)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(os.path.join(folder, f"{name}.pdf"), pagesize=letter)
    elements = []

    left_heading2 = ParagraphStyle(
        "LeftHeading2", parent=styles["Heading2"], alignment=TA_LEFT
    )
    elements.append(
        Paragraph(to_camel_case(name.split("__")[0].replace("_", " ")), left_heading2)
    )

    elements.append(Spacer(1, 24))

    max_cols = 6

    for main_attr, nested_dict in data.items():
        header = main_attr.strip('" ')

        columns = list(nested_dict.keys())
        clean_columns = [col.strip('" ') for col in columns]

        # Get row labels from first nested dict value
        example_values = nested_dict[columns[0]]
        row_labels = list(example_values.keys())

        # Split columns in chunks of max_cols
        for i in range(0, len(columns), max_cols):
            chunk_cols = columns[i : i + max_cols]
            chunk_clean_cols = clean_columns[i : i + max_cols]

            table_data = [["", *chunk_clean_cols]]

            for row_label in row_labels:
                row = [row_label]
                for col in chunk_cols:
                    val = nested_dict[col].get(row_label)
                    if isinstance(val, float):
                        val_str = f"{val * 100:.2f}%"
                    elif isinstance(val, bool):
                        val_str = "✓" if val else "✗"
                    else:
                        val_str = str(val)
                    row.append(val_str)
                table_data.append(row)

            table = Table(table_data)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (1, 0), (-1, 0), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ]
                )
            )

            elements.append(
                Paragraph(to_camel_case(header.split("__")[0]), left_heading2)
            )
            elements.append(Spacer(1, 12))
            elements.append(table)
            elements.append(Spacer(1, 24))

    doc.build(elements)
    logger.info(f"PDF saved to {doc.filename}")


def preprocessing_json_to_pdf(folder, name, path):
    os.makedirs(folder, exist_ok=True)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(os.path.join(folder, f"{name}.pdf"), pagesize=letter)
    elements = []

    # Prepare header (keys) and one row of values
    headers = list(data.keys())
    values = []
    for val in data.values():
        if isinstance(val, float):
            values.append(f"{val * 100:.2f}%")  # Format float as percentage
        else:
            values.append(str(val))

    # Build table data: one row for headers, one for values
    table_data = [headers, values]

    table = Table(table_data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    left_heading2 = ParagraphStyle(
        "LeftHeading2", parent=styles["Heading2"], alignment=TA_LEFT
    )
    elements.append(Paragraph(to_camel_case(name.split("__")[0]), left_heading2))
    elements.append(Spacer(1, 12))
    elements.append(table)
    elements.append(Spacer(1, 24))

    doc.build(elements)
    logger.info(f"PDF saved to: {os.path.join(folder, f'{name}.pdf')}")


def create_report_data(temp_dir, title, dictionary):
    for name, value in dictionary.items():
        if is_json_string(value):
            json_to_pdf2(temp_dir, title, name, value)
        elif is_csv(value):
            csv_to_pdf_table(temp_dir, title, name, value)
        else:
            graph_creator(temp_dir, title, name, value)


def create_report(temp_dir: str, file_name: str):
    if os.path.isdir(temp_dir):
        folders = [
            f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))
        ]

        # Sort by creation time
        folders.sort(key=lambda f: os.path.getctime(os.path.join(temp_dir, f)))

        for dir in folders:
            PDFCreator2(temp_dir, dir, file_name)
    else:
        logger.info("ReportData does not exist")
