import pygame
import json
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
NODE_RADIUS = 20
BG_COLOR = (255, 255, 255)
NODE_COLOR = (0, 128, 255)
EDGE_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 0, 0)
ARROW_COLOR = (255, 0, 0)  # Arrow color for visibility
ARROW_OUTLINE_COLOR = (0, 0, 0)  # Outline color for arrows
DIRECTION_CIRCLE_COLOR = (0, 0, 0)  # Color of the direction circle
FPS = 60
ARROW_SIZE = 10  # Size of the arrowhead
LINE_WIDTH = 4  # Thicker line for edges
DIRECTION_CIRCLE_RADIUS = 5  # Radius of the direction circle

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tree Editor with Cubic Bezier Curves")
clock = pygame.time.Clock()

# Data Structures
class Node:
    def __init__(self, pos, node_id):
        self.pos = pos
        self.node_id = node_id
        self.children = []

    def draw(self, screen, color=NODE_COLOR):
        pygame.draw.circle(screen, color, self.pos, NODE_RADIUS)
        font = pygame.font.SysFont(None, 24)
        text = font.render(str(self.node_id), True, (255, 255, 255))
        screen.blit(text, (self.pos[0] - text.get_width() // 2, self.pos[1] - text.get_height() // 2))

    def add_child(self, child_node):
        if child_node not in self.children:
            self.children.append(child_node)

    def remove_child(self, child_node):
        if child_node in self.children:
            self.children.remove(child_node)

    def is_clicked(self, mouse_pos):
        return math.hypot(self.pos[0] - mouse_pos[0], self.pos[1] - mouse_pos[1]) <= NODE_RADIUS

class TreeEditor:
    def __init__(self):
        self.nodes = []
        self.edges = {}
        self.selected_node = None
        self.node_counter = 0
        self.is_dragging = False  # Track dragging state
        self.drag_offset = (0, 0)  # Offset for dragging

    def create_node(self, pos):
        node = Node(pos, self.node_counter)
        self.node_counter += 1
        self.nodes.append(node)

    def connect_nodes(self, parent, child):
        # Check if the connection already exists
        if child in self.edges.get(parent, []):
            # Remove the connection if it already exists
            parent.remove_child(child)
            self.edges[parent].remove(child)
            if not self.edges[parent]:  # Remove the entry if no connections exist
                del self.edges[parent]
        else:
            # Create a new connection
            parent.add_child(child)
            if parent not in self.edges:
                self.edges[parent] = []
            self.edges[parent].append(child)

    def get_clicked_node(self, mouse_pos):
        for node in self.nodes:
            if node.is_clicked(mouse_pos):
                return node
        return None

    def draw_cubic_bezier_curve(self, screen, start, end, control1, control2):
        # Draw a cubic Bezier curve from start to end using control points
        num_points = 100  # Number of points to create the curve
        for i in range(num_points):
            t = i / (num_points - 1)
            x = (1 - t) ** 3 * start[0] + \
                3 * (1 - t) ** 2 * t * control1[0] + \
                3 * (1 - t) * t ** 2 * control2[0] + \
                t ** 3 * end[0]
            y = (1 - t) ** 3 * start[1] + \
                3 * (1 - t) ** 2 * t * control1[1] + \
                3 * (1 - t) * t ** 2 * control2[1] + \
                t ** 3 * end[1]
            if i > 0:  # Draw line segment from the previous point
                pygame.draw.line(screen, EDGE_COLOR, (prev_x, prev_y), (x, y), LINE_WIDTH)
            prev_x, prev_y = x, y

    def draw_arrow(self, screen, start, end):
        # Control points are set to create a smoother horizontal connection
        control1 = (start[0] + (end[0] - start[0]) / 3, start[1])  # First control point
        control2 = (end[0] - (end[0] - start[0]) / 3, end[1])      # Second control point
        self.draw_cubic_bezier_curve(screen, start, end, control1, control2)

        # Calculate the angle for the arrowhead
        angle = math.atan2(end[1] - control2[1], end[0] - control2[0])
        arrow_end1 = (end[0] - ARROW_SIZE * math.cos(angle - math.pi / 6),
                      end[1] - ARROW_SIZE * math.sin(angle - math.pi / 6))
        arrow_end2 = (end[0] - ARROW_SIZE * math.cos(angle + math.pi / 6),
                      end[1] - ARROW_SIZE * math.sin(angle + math.pi / 6))

        # Draw the arrowhead with outline
        pygame.draw.polygon(screen, ARROW_OUTLINE_COLOR, [end, arrow_end1, arrow_end2])
        pygame.draw.polygon(screen, ARROW_COLOR, [end, arrow_end1, arrow_end2])

        # Draw a black circle at the child node position to indicate the direction
        pygame.draw.circle(screen, DIRECTION_CIRCLE_COLOR, end, DIRECTION_CIRCLE_RADIUS)

    def draw(self, screen):
        # Draw edges
        for parent, children in self.edges.items():
            for child in children:
                self.draw_arrow(screen, parent.pos, child.pos)

        # Draw nodes
        for node in self.nodes:
            if node == self.selected_node:
                node.draw(screen, HIGHLIGHT_COLOR)  # Highlight the selected node
            else:
                node.draw(screen)

    def delete_node(self, node_to_delete):
        # Remove the node from the nodes list
        if node_to_delete in self.nodes:
            self.nodes.remove(node_to_delete)
            # Also remove any edges to this node from its parent nodes
            for parent, children in self.edges.items():
                if node_to_delete in children:
                    children.remove(node_to_delete)
            # Also remove the node as a child from its parents
            for child in node_to_delete.children:
                child.remove_child(node_to_delete)
            # Remove from edges
            if node_to_delete in self.edges:
                del self.edges[node_to_delete]

    def export_to_json(self):
        tree_data = {}
        for node in self.nodes:
            tree_data[node.node_id] = {
                'position': node.pos,
                'children': [child.node_id for child in node.children]
            }
        with open('tree_structure.json', 'w') as f:
            json.dump(tree_data, f, indent=4)
        print("Tree structure exported to tree_structure.json")


def main():
    editor = TreeEditor()
    running = True

    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_node = editor.get_clicked_node(mouse_pos)

                if event.button == 1:  # Left click
                    if clicked_node:
                        if editor.selected_node and editor.selected_node != clicked_node:
                            # Connect the selected node to the clicked node (create an edge)
                            editor.connect_nodes(editor.selected_node, clicked_node)
                            editor.selected_node = None
                        else:
                            # Select the node
                            editor.selected_node = clicked_node
                            # Start dragging
                            editor.is_dragging = True
                            # Calculate the offset
                            editor.drag_offset = (clicked_node.pos[0] - mouse_pos[0], clicked_node.pos[1] - mouse_pos[1])
                    else:
                        # If clicking on the background, deselect the node
                        editor.selected_node = None
                        # Do not create a new node if a node is currently selected
                        if not editor.selected_node:
                            editor.create_node(mouse_pos)

                elif event.button == 3:  # Right click
                    if clicked_node:
                        editor.delete_node(clicked_node)  # Delete the clicked node

            elif event.type == pygame.MOUSEBUTTONUP:
                # Stop dragging
                editor.is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if editor.is_dragging and editor.selected_node:
                    # Update the position of the selected node
                    mouse_x, mouse_y = event.pos
                    editor.selected_node.pos = (mouse_x + editor.drag_offset[0], mouse_y + editor.drag_offset[1])

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    # Export to JSON when "S" key is pressed
                    editor.export_to_json()

        # Render everything
        editor.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
