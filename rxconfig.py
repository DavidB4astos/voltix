import reflex as rx

config = rx.Config(
    app_name="voltix",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                accent_color="cyan",
                gray_color="slate",
                radius="large",
                appearance="light",
            ),
        ),
    ]
)