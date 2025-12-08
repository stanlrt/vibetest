import asyncio
import json

from browser_use import ActionResult, Browser
from browser_use.browser.events import ClickElementEvent


def register_tools(tools):
    """Register all custom tools with the Tools instance"""

    @tools.action(description='Very useful for hidden inputs, where the visible element is not the actual input. It clicks an element at its center coordinates using mouse actions instead of DOM click, mimicking a real user.')
    async def click_element_visually(index: int, browser_session: Browser) -> ActionResult:
        """
        Custom action to click an element by getting its coordinates and using mouse.click().
        This bypasses normal DOM click and can work with elements that are hard to click normally.

        Args:
            index: The element index from the DOM
            browser_session: The browser session
        """
        try:
            if index == 0:
                return ActionResult(error='Cannot click on element with index 0. If there are no interactive elements use wait(), refresh(), etc.')

            # Get the element by index using browser-use's method
            node = await browser_session.get_element_by_index(index)
            if node is None:
                return ActionResult(error=f'Element index {index} not available - page may have changed. Try refreshing browser state.')

            # Get the current page
            page = await browser_session.get_current_page()
            if page is None:
                return ActionResult(error='Failed to get current page')

            # Get xpath from the node
            xpath = node.xpath
            if not xpath:
                return ActionResult(error=f'Element at index {index} has no xpath')

            # Ensure xpath starts with / for document.evaluate
            if not xpath.startswith('/'):
                xpath = '/' + xpath

            # Use JavaScript to get the element's bounding box using xpath
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

            # Handle case where result is returned as JSON string instead of dict
            if isinstance(coords, str):
                try:
                    coords = json.loads(coords)
                except json.JSONDecodeError:
                    return ActionResult(error=f'Failed to parse coordinates for element at index {index}')

            if not coords or not isinstance(coords, dict):
                return ActionResult(error=f'Failed to get coordinates for element at index {index}')

            x = int(coords.get('x', 0))
            y = int(coords.get('y', 0))

            if x == 0 or y == 0:
                return ActionResult(error=f'Invalid coordinates for element at index {index}')

            # Click at the calculated coordinates using Playwright mouse
            # In browser-use, page.mouse may be a coroutine that returns the Mouse object
            mouse = page.mouse
            if hasattr(mouse, '__await__'):
                mouse = await mouse
            await mouse.click(x, y)  # type: ignore[union-attr]

            return ActionResult(
                extracted_content=f'Successfully clicked element at index {index} using coordinates (x={x}, y={y})',
            )

        except Exception as e:
            return ActionResult(error=f'Failed to click element by coordinates: {str(e)}')

    @tools.action(description='Click an element only if it is actually visible (not hidden by opacity, display, visibility, or outside viewport). Uses browser-use internal click mechanism.')
    async def click_element_if_visible(index: int, browser_session: Browser) -> ActionResult:
        """
        Click an element only if it passes visibility checks:
        - opacity is not 0
        - display is not 'none'
        - visibility is not 'hidden'
        - element is within the viewport bounds

        Uses browser-use's internal ClickElementEvent for the actual click.

        Args:
            index: The element index from the DOM
            browser_session: The browser session
        """
        try:
            if index == 0:
                return ActionResult(error='Cannot click on element with index 0. If there are no interactive elements use wait(), refresh(), etc.')

            # Get the element by index using browser-use's method (same as internal _click_by_index)
            node = await browser_session.get_element_by_index(index)
            if node is None:
                return ActionResult(error=f'Element index {index} not available - page may have changed. Try refreshing browser state.')

            # Get the element's XPath for visibility check
            xpath = node.xpath
            if not xpath:
                return ActionResult(error=f'Element at index {index} has no XPath')

            # Ensure xpath starts with / for document.evaluate
            if not xpath.startswith('/'):
                xpath = '/' + xpath

            # Get the current page
            page = await browser_session.get_current_page()
            if page is None:
                return ActionResult(error='Failed to get current page')

            # JavaScript to check visibility comprehensively
            js_visibility_check = """
                (xpath) => {
                    const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (!element) {
                        return { visible: false, reason: 'Element not found in DOM' };
                    }

                    const style = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();

                    // Check if element has zero dimensions
                    if (rect.width === 0 || rect.height === 0) {
                        return { visible: false, reason: 'Element has zero width or height' };
                    }

                    // Check opacity (including parent opacity)
                    let currentElement = element;
                    while (currentElement) {
                        const currentStyle = window.getComputedStyle(currentElement);
                        if (parseFloat(currentStyle.opacity) === 0) {
                            return { visible: false, reason: 'Element or ancestor has opacity 0' };
                        }
                        currentElement = currentElement.parentElement;
                    }

                    // Check display
                    if (style.display === 'none') {
                        return { visible: false, reason: 'Element has display: none' };
                    }

                    // Check visibility
                    if (style.visibility === 'hidden' || style.visibility === 'collapse') {
                        return { visible: false, reason: 'Element has visibility: hidden or collapse' };
                    }

                    // Check if element is within viewport
                    const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
                    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

                    const isInViewport = (
                        rect.top < viewportHeight &&
                        rect.bottom > 0 &&
                        rect.left < viewportWidth &&
                        rect.right > 0
                    );

                    if (!isInViewport) {
                        return { 
                            visible: false, 
                            reason: `Element is outside viewport (rect: top=${rect.top}, bottom=${rect.bottom}, left=${rect.left}, right=${rect.right}, viewport: ${viewportWidth}x${viewportHeight})` 
                        };
                    }

                    return { visible: true };
                }
            """

            visibility_result = await page.evaluate(js_visibility_check, xpath)

            # Handle case where result is returned as JSON string instead of dict
            if isinstance(visibility_result, str):
                try:
                    visibility_result = json.loads(visibility_result)
                except json.JSONDecodeError:
                    return ActionResult(error=f'Failed to parse visibility result for element at index {index}')

            if not visibility_result or not isinstance(visibility_result, dict):
                return ActionResult(error=f'Failed to check visibility for element at index {index}')

            if not visibility_result.get('visible', False):
                reason = visibility_result.get('reason', 'Unknown reason')
                return ActionResult(
                    error=f'Element at index {index} is not visible: {reason}',
                )

            # Element is visible, use browser-use's internal click mechanism via event bus
            try:
                event = browser_session.event_bus.dispatch(
                    ClickElementEvent(node=node))
                await event
                click_metadata = await event.event_result(raise_if_any=True, raise_if_none=False)
            except Exception as click_error:
                return ActionResult(error=f'Click event failed: {str(click_error)}')

            # Check if result contains validation error
            if isinstance(click_metadata, dict) and 'validation_error' in click_metadata:
                return ActionResult(error=click_metadata['validation_error'])

            return ActionResult(
                extracted_content=f'Element at index {index} was visible and clicked successfully',
                metadata=click_metadata if isinstance(
                    click_metadata, dict) else None,
            )

        except Exception as e:
            return ActionResult(error=f'Failed to click element if visible: {str(e)}')

    @tools.action(description='Wait for exactly 400ms (Doherty threshold) to simulate natural human interaction timing. Use this instead of the standard wait action for realistic human-like delays.')
    async def human_wait() -> ActionResult:
        """
        Wait for exactly 400ms - the Doherty threshold.

        The Doherty threshold represents the response time at which users feel a system is responding instantly.
        This creates natural, human-like pauses between actions.

        Unlike the standard wait() action which has variable timing logic,
        this always waits exactly 400ms.
        """
        await asyncio.sleep(0.4)
        return ActionResult(
            extracted_content='Waited 400ms (Doherty threshold)',
        )


# Import and register tools after creating the Tools instance
# register_tools(tools)

# @tools.action(description='Directly set the value attribute of an input element by index and dispatch input/change events')
# async def set_input_value(index: int, value: str, browser_session: Browser) -> ActionResult:
#     """
#     Custom action to directly set the value attribute of an input element.
#     This bypasses normal typing and directly sets the value using JavaScript,
#     then dispatches appropriate events to trigger any listeners.

#     Args:
#         index: The element index from the DOM
#         value: The value to set
#         browser_session: The browser session
#     """
#     try:
#         # Get the DOM element by index
#         dom_element = await browser_session.get_dom_element_by_index(index)

#         if dom_element is None:
#             return ActionResult(error=f'No element found at index {index}')

#         # Verify it's an input element
#         if dom_element.tag_name.lower() != 'input':
#             return ActionResult(error=f'Element at index {index} is not an input element (found {dom_element.tag_name})')

#         # Get the element's XPath for selection
#         xpath = dom_element.xpath

#         if not xpath:
#             return ActionResult(error=f'Element at index {index} has no XPath')

#         # Get the current page
#         page = await browser_session.get_current_page()

#         if page is None:
#             return ActionResult(error='Failed to get current page')

#         # Use JavaScript to set the value and dispatch events
#         # XPath is used to locate the element, then we set value and trigger events
#         js_code = """
#             (xpath, value) => {
#                 const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
#                 if (element) {
#                     element.value = value;
#                     element.dispatchEvent(new Event('input', { bubbles: true }));
#                     element.dispatchEvent(new Event('change', { bubbles: true }));
#                     return true;
#                 }
#                 return false;
#             }
#         """

#         result = await page.evaluate(js_code, xpath, value)

#         if not result:
#             return ActionResult(error=f'Failed to find element with XPath: {xpath}')

#         return ActionResult(
#             success=True,
#             extracted_content=f'Successfully set value "{value}" on input element at index {index}',
#             include_in_memory=True
#         )

#     except Exception as e:
#         return ActionResult(error=f'Failed to set input value: {str(e)}')
