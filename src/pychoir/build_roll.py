def generate_section_roll(section, rehid, rehdesc, attendance, message):
    table = [
        [
            {'.b': 'id'},
            {'.b': 'Name'},
            {'.b': 'Standing'},
            {'.b': 'Signature'}
        ],
    ]
    for row in attendance.iter_rows(named=True):
        table.append(
            [
                row['id'],
                row['name'],
                row['attendance'],
                '',
            ]
        )

    document = {
        "style": {
            "page_size": "letter", "margin": [70, 60],
            "s": 10, "c": 0.3, "f": "Courier", "text_align": "j",
            "margin_bottom": 6
        },
        "formats": {
            "title": {"s": 18, "b": True, "text_align": "c", "margin_bottom": 10}
        },
        "sections": [
            {
                "content": [
                    {".": section + " Attendance for Rehearsal " + rehid +
                        ",\n" + rehdesc, "style": "title"},
                    {
                        ".": message
                    },
                    {  # Table in here
                        "widths": [1, 4, 1.8, 8],
                        "table": table
                    }
                ]
            },
        ]
    }
    return document
