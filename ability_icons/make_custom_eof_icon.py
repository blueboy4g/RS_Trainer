from PIL import Image

eof_icons = [
#"30px-Fractured_Staff_Of_Armadyl.png",
#"30px-Omni_Guard.png"
    "30px-Death_Guard.png",
    "30px-Dark_Bow.png",
    "30px-Dragon_claw.png",
    "30px-Eldritch_Crossbow.png",
    "30px-Guthix_Staff.png",
    "30px-Iban's_staff.png",
    "30px-Seren_godbow.png",
    "30px-Zamorak_Bow.png",
    "30px-Dragon_Scimitar.png",
    "30px-Gloomfire_Bow.png",
    "30px-Legatus_Emberstaff.png",
    "30px-Varanus_Mercy.png",
    "30px-Zamorak_Staff.png",
    "30px-Dragon_2h_Sword.png",
    "30px-Dragon_Dagger.png",
    "30px-Dragon_Longsword.png",
    "30px-Dragon_Halberd.png",
    "30px-Granite_Maul.png",
    "30px-Statius_Warhammer.png",
    "30px-Armadyl_Battlestaff.png",
    "30px-Staff_of_Light.png",
    "30px-Annihilation.png",
]

for icon in eof_icons:
    print(f"Processing {icon}...")
    # Hardcoded paths
    image_a_path = "30px-Essence_of_Finality.png"
    image_b_path = icon
    output_path = icon[:-4] + "_In_EOF.png"

    # Load images
    img_a = Image.open(image_a_path)
    img_b = Image.open(image_b_path)

    img_b = img_b.resize((int(60), int(60)), Image.Resampling.LANCZOS)
    img_a = img_a.resize((int(60), int(60)), Image.Resampling.LANCZOS)

    a_scaled = img_a
    b_scaled = img_b

    # Calculate size of output canvas
    canvas_width = max(a_scaled.width, b_scaled.width)
    canvas_height = max(a_scaled.height, b_scaled.height)
    # Resize images
    a_scaled = img_a.resize((int(img_a.width * 0.75), int(img_a.height * 0.75)))
    b_scaled = img_b.resize((int(img_b.width * 0.8), int(img_b.height * 0.8)))


    # Expand canvas if needed to fit bottom-right image
    canvas_width = max(canvas_width, b_scaled.width)
    canvas_height = max(canvas_height, b_scaled.height)

    # Create a new transparent image
    output = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 255))

    # Paste images
    output.paste(a_scaled, (0, 0), a_scaled.convert("RGBA"))
    output.paste(b_scaled, (canvas_width - b_scaled.width, canvas_height - b_scaled.height), b_scaled.convert("RGBA"))

    # Save result
    output.save(output_path)
    print(f"Saved to {output_path}")
