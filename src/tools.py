from browser_use import ActionResult, Browser


def register_tools(tools):
    """Register all custom tools with the Tools instance"""

    @tools.action(description='Click an element at its center coordinates using mouse actions instead of DOM click')
    async def click_element_visually(index: int, browser_session: Browser) -> ActionResult:
        """
        Custom action to click an element by getting its coordinates and using mouse.click().
        This bypasses normal DOM click and can work with elements that are hard to click normally.

        Args:
            index: The element index from the DOM
            browser_session: The browser session
        """
        try:
            # Get the DOM element by index
            dom_element = await browser_session.get_dom_element_by_index(index)

            if dom_element is None:
                return ActionResult(error=f'No element found at index {index}')

            # Get the element's XPath for selection
            xpath = dom_element.xpath

            if not xpath:
                return ActionResult(error=f'Element at index {index} has no XPath')

            # Get the current page
            page = await browser_session.get_current_page()

            if page is None:
                return ActionResult(error='Failed to get current page')

            # Use JavaScript to get the element's bounding box and calculate center coordinates
            js_code = """
                (xpath) => {
                    const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element) {
                        const rect = element.getBoundingClientRect();
                        return {
                            x: rect.left + rect.width / 2,
                            y: rect.top + rect.height / 2,
                            width: rect.width,
                            height: rect.height
                        };
                    }
                    return null;
                }
            """

            coords = await page.evaluate(js_code, xpath)

            if not coords or not isinstance(coords, dict):
                return ActionResult(error=f'Failed to get coordinates for element at index {index}')

            # Convert coordinates to integers
            x = int(coords.get('x', 0))
            y = int(coords.get('y', 0))

            if x == 0 or y == 0:
                return ActionResult(error=f'Invalid coordinates for element at index {index}')

            # Get the mouse object and click at the calculated coordinates
            mouse = await page.mouse
            await mouse.click(x=x, y=y)

            return ActionResult(
                success=True,
                extracted_content=f'Successfully clicked element at index {index} using coordinates (x={x}, y={y})',
                include_in_memory=True
            )

        except Exception as e:
            return ActionResult(error=f'Failed to click element by coordinates: {str(e)}')
