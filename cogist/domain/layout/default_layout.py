"""Default Layout Algorithm - Domain Layer

Pure algorithm implementation, no UI dependencies.
Based on the original default_layout_demo.py logic.
"""

from __future__ import annotations

from cogist.domain.layout.base import (
    DEFAULT_LAYOUT_CONFIG,
    BaseLayout,
    DefaultLayoutConfig,
    LayoutMetadata,
)
from cogist.domain.layout.registry import layout_registry


class DefaultLayout(BaseLayout):
    """
    Default style layout algorithm.

    Features:
    1. Root node centered
    2. Left and right branches
    3. Auto balance left/right nodes
    4. Smart spacing adjustment

    This is a pure domain algorithm that works with Node entities.
    It calculates positions but doesn't render anything.
    """

    METADATA = LayoutMetadata(
        name="Default",
        description="左右平衡式布局（Default 风格）",
        category="general",
        supports_mixed=False,
    )

    def __init__(self, config: DefaultLayoutConfig | None = None):
        """
        Initialize layout algorithm.

        Args:
            config: Layout configuration (uses default if not provided)
        """
        super().__init__(config or DEFAULT_LAYOUT_CONFIG)

    def _get_default_config(self) -> DefaultLayoutConfig:
        """Return default configuration for DefaultLayout"""
        return DEFAULT_LAYOUT_CONFIG

    def _get_level_spacing_for_depth(self, depth: int) -> float:
        """
        Get horizontal spacing between parent and child based on child's depth.

        Args:
            depth: Child node's depth in tree (not parent's)

        Returns:
            Horizontal spacing for this parent-child relationship
        """
        # If style_config is provided, read spacing from role_styles based on child's role
        if self.config.style_config and hasattr(self.config.style_config, 'role_styles'):
            from cogist.domain.styles import NodeRole

            # Map child depth to role
            role_map = {0: NodeRole.ROOT, 1: NodeRole.PRIMARY, 2: NodeRole.SECONDARY}
            child_role = role_map.get(depth, NodeRole.TERTIARY)

            # Get spacing from child's role style
            if child_role in self.config.style_config.role_styles:
                role_style = self.config.style_config.role_styles[child_role]
                return role_style.parent_child_spacing

        # Fallback to config's level_spacing
        return self.config.level_spacing

    def _get_sibling_spacing_for_depth(self, depth: int) -> float:
        """
        Get sibling spacing based on node depth.

        Args:
            depth: Node depth in tree

        Returns:
            Sibling spacing for this depth
        """
        # If style_config is provided, read spacing from role_styles based on node's role
        if self.config.style_config and hasattr(self.config.style_config, 'role_styles'):
            from cogist.domain.styles import NodeRole

            # Map node depth to role
            role_map = {0: NodeRole.ROOT, 1: NodeRole.PRIMARY, 2: NodeRole.SECONDARY}
            node_role = role_map.get(depth, NodeRole.TERTIARY)

            # Get spacing from node's role style
            if node_role in self.config.style_config.role_styles:
                role_style = self.config.style_config.role_styles[node_role]
                return role_style.sibling_spacing

        # Fallback to config's sibling_spacing
        return self.config.sibling_spacing

    def _calculate_aligned_edge(
        self,
        parent_node,
        child_nodes: list,
        direction: int,
    ) -> float:
        """
        Calculate the aligned edge position for child nodes.

        This ensures all siblings align on the side closest to parent.

        Args:
            parent_node: The parent node
            child_nodes: List of child nodes to align
            direction: -1 for left side, 1 for right side

        Returns:
            The x-coordinate where children should align their edges
        """
        # Get horizontal spacing for this parent-child relationship
        level_spacing = self._get_level_spacing_for_depth(parent_node.depth + 1)

        # Use visual width/height (including border expansion)
        parent_border = getattr(parent_node, 'border_width', 0)
        parent_visual_width = parent_node.width + parent_border * 2

        aligned_edge_x = 0.0  # Will be set based on direction

        # For left side (direction=-1): align right edge of children
        # For right side (direction=1): align left edge of children
        if direction == -1:  # Left side
            # Parent's visual left edge
            parent_visual_left = parent_node.position[0] - parent_visual_width / 2.0
            aligned_edge_x = parent_visual_left - level_spacing
        else:  # Right side
            # Parent's visual right edge
            parent_visual_right = parent_node.position[0] + parent_visual_width / 2.0
            aligned_edge_x = parent_visual_right + level_spacing

        return aligned_edge_x

    def _calculate_node_position(
        self,
        node,
        aligned_edge_x: float,
        direction: int,
    ) -> tuple[float, float]:
        """
        Calculate node center position based on aligned edge.

        Args:
            node: The node to position
            aligned_edge_x: The x-coordinate where the node's visual edge should align
            direction: -1 for left side, 1 for right side

        Returns:
            Tuple of (node_x, node_y) - node center position
        """
        # Calculate visual half width (including border expansion)
        node_border = getattr(node, 'border_width', 0)
        node_visual_half_width = (node.width + node_border * 2) / 2.0

        if direction == -1:  # Left side - align right visual edge
            # Visual center = aligned_edge_x - visual_half_width
            node_x = aligned_edge_x - node_visual_half_width
        else:  # Right side - align left visual edge
            # Visual center = aligned_edge_x + visual_half_width
            node_x = aligned_edge_x + node_visual_half_width

        return node_x

    def _get_visual_height(self, node) -> float:
        """
        Get the visual height of a node (including border expansion).

        Args:
            node: The node to measure

        Returns:
            Visual height including border on top and bottom
        """
        border_width = getattr(node, 'border_width', 0)
        return node.height + border_width * 2

    def layout(
        self,
        root_node,
        canvas_width: float = 1200.0,
        canvas_height: float = 800.0,
        context: dict | None = None,
    ) -> None:
        """
        Apply Default layout to a node tree.

        Args:
            root_node: The root node of the mind map
            canvas_width: Canvas width for centering
            canvas_height: Canvas height for centering
            context: Optional context information
                     - focused_node_id: ID of the currently focused/selected node
        """
        # Extract focused_node_id from context if provided
        focused_node_id = None
        if context and "focused_node_id" in context:
            focused_node_id = context["focused_node_id"]

        # Node sizes are already set from UI layer measurement
        # No need to estimate - we use actual rendered sizes

        # Root node position: place at scene center (0, 0) on first layout
        # This prevents unnecessary view jumping during style changes
        # Note: NodeItem uses center as origin, so position is the center
        # CRITICAL: Scene coordinate system has origin at (0, 0), which is the center of sceneRect
        # Only set position if root hasn't been positioned yet (default is (0.0, 0.0))
        if root_node.is_root and root_node.position == (0.0, 0.0):
            # First layout - explicitly place root at scene center
            # This makes it clear that we're intentionally positioning it
            root_node.position = (0.0, 0.0)

        children = root_node.children
        if not children:
            return

        # Find which top-level child contains the focused node
        locked_side_child = None
        if focused_node_id:
            locked_side_child = self._find_top_level_child_with_focus(
                root_node, focused_node_id
            )

        # Children order is preserved from the children list
        children = root_node.children

        # Balance distribution: intelligently assign nodes to left/right for height balance
        left_children, right_children = self._balance_branches(
            children, locked_side_child, parent_node=root_node
        )

        # Layout left branch
        if left_children:
            self._layout_side(left_children, root_node, canvas_height, -1)

        # Layout right branch
        if right_children:
            self._layout_side(right_children, root_node, canvas_height, 1)

        # No need to call _center_layout - already centered during layout

    def _find_top_level_child_with_focus(self, root_node, focused_node_id: str):
        """
        Find which top-level child (direct child of root) contains the focused node.

        Args:
            root_node: The root node
            focused_node_id: ID of the focused node

        Returns:
            The top-level child node that contains the focused node, or None if not found
        """

        def contains_node(node, target_id):
            """Recursively check if a node tree contains the target node."""
            if node.id == target_id:
                return True
            return any(contains_node(child, target_id) for child in node.children)

        # Check each direct child of root
        for child in root_node.children:
            if contains_node(child, focused_node_id):
                return child

        return None

    def _calculate_subtree_height(self, node) -> float:
        """
        Calculate the total vertical height a node and its subtree will occupy.

        Args:
            node: The node to calculate height for

        Returns:
            Total height including all descendants and spacing
        """
        if not node.children:
            return self._get_visual_height(node)

        # Get spacing for node's children (which are at depth = node.depth + 1)
        # Use the maximum depth among children subtrees
        sibling_spacing = self._get_sibling_spacing_for_nodes(node.children)

        # Calculate heights of all children subtrees
        child_heights = [
            self._calculate_subtree_height(child) for child in node.children
        ]

        # Total height = sum of child heights + spacing between them
        total_child_height = sum(child_heights)
        total_spacing = (len(node.children) - 1) * sibling_spacing

        # The node itself takes max(visual_height, total_child_height)
        # because children are centered around the node
        return max(self._get_visual_height(node), total_child_height + total_spacing)

    def _get_max_subtree_depth(self, node) -> int:
        """
        Get the maximum depth in a subtree.

        Args:
            node: Root of the subtree

        Returns:
            Maximum depth in the subtree
        """
        if not node.children:
            return node.depth

        max_child_depth = max(
            self._get_max_subtree_depth(child) for child in node.children
        )
        return max_child_depth

    def _get_sibling_spacing_for_nodes(self, nodes: list, parent_depth: int | None = None) -> float:
        """
        Get the appropriate sibling spacing for a list of nodes.

        Args:
            nodes: List of sibling nodes

        Returns:
            Sibling spacing based on the nodes' depth level
        """
        if not nodes:
            return self.sibling_spacing

        # Use spacing at the nodes' own depth level
        # For multiple siblings: use their depth
        # For children list: use children's depth (which determines spacing between them)
        return self._get_sibling_spacing_for_depth(nodes[0].depth)

    def _balance_branches(
        self, nodes: list, locked_side_child=None, parent_node=None
    ) -> tuple[list, list]:
        """
        Intelligently distribute nodes to left and right branches for height balance.

        Strategy:
        1. Lock the side of the focused node's top-level ancestor
        2. Distribute remaining nodes to achieve balance
        3. Only move non-locked nodes between sides

        Args:
            nodes: List of child nodes to distribute
            locked_side_child: The top-level child that must stay on its current side
            parent_node: The parent node (used to determine left/right sides)

        Returns:
            Tuple of (left_children, right_children)
        """
        if not nodes:
            return ([], [])

        # Use parent X position as the dividing line between left and right
        parent_x = parent_node.position[0] if parent_node else 600.0

        if len(nodes) == 1:
            # Single node: determine side based on current position relative to parent
            if locked_side_child and nodes[0] == locked_side_child:
                # Locked node: keep on its current side
                # Rule 2: Compare center points, not left edge positions
                node_center_x = nodes[0].position[0] + nodes[0].width / 2
                parent_center_x = (
                    parent_x + parent_node.width / 2 if parent_node else parent_x
                )
                if node_center_x < parent_center_x:
                    return (nodes, [])
                else:
                    return ([], nodes)
            # Default to right side for first child (Default style)
            return ([], nodes)

        # Step 1: Determine original sides based on current X positions relative to parent
        parent_x_estimate = parent_node.position[0] if parent_node else 600.0

        left_original = []
        right_original = []

        for node in nodes:
            # For new nodes (position[0] == 0), default to right side
            # For existing nodes, use their current position
            if node.position[0] == 0.0 and not node.is_root:
                # New node: default to right side
                right_original.append(node)
            else:
                # Rule 2: Compare center points, not left edge positions
                node_center_x = node.position[0] + node.width / 2
                parent_center_x = (
                    parent_x_estimate + parent_node.width / 2
                    if parent_node
                    else parent_x_estimate
                )
                if node_center_x < parent_center_x:
                    left_original.append(node)
                else:
                    right_original.append(node)

        # Step 2: If we have a locked child, ensure it stays on its original side
        # Only lock if the locked_child is directly in our nodes list AND has children
        # (locking leaf nodes is unnecessary since they have no subtree to preserve)
        locked_node_for_rebalance = None  # Default: no locked node

        if (
            locked_side_child
            and locked_side_child in nodes
            and locked_side_child.children
        ):
            if locked_side_child in left_original:
                pass  # Locked node is on the left side
            elif locked_side_child in right_original:
                pass  # Locked node is on the right side
            locked_node_for_rebalance = (
                locked_side_child  # Only set if we're actually locking
            )

        # Step 3: Calculate heights for each side
        left_heights = [self._calculate_subtree_height(node) for node in left_original]
        right_heights = [
            self._calculate_subtree_height(node) for node in right_original
        ]

        # Use spacing based on the maximum depth among all root's children subtrees
        # This ensures adjacent subtrees use the deepest level's spacing
        level1_spacing = self._get_sibling_spacing_for_nodes(left_original + right_original)

        left_total = (
            sum(left_heights) + (len(left_original) - 1) * level1_spacing
            if left_original
            else 0
        )
        right_total = (
            sum(right_heights) + (len(right_original) - 1) * level1_spacing
            if right_original
            else 0
        )

        # Step 4: Rebalance - only move non-locked nodes
        left_children = list(left_original)
        right_children = list(right_original)
        left_height = left_total
        right_height = right_total

        # Determine which side is taller and try to move nodes from it
        if left_height > right_height:
            # Move nodes from left to right
            self._rebalance_branches(
                from_side=left_children,
                to_side=right_children,
                locked_node=locked_node_for_rebalance,
                from_height=left_height,
                to_height=right_height,
            )
        else:
            # Move nodes from right to left
            self._rebalance_branches(
                from_side=right_children,
                to_side=left_children,
                locked_node=locked_node_for_rebalance,
                from_height=right_height,
                to_height=left_height,
            )

        return (left_children, right_children)

    def _rebalance_branches(
        self,
        from_side: list,
        to_side: list,
        locked_node: object,
        from_height: float,
        to_height: float,
    ) -> None:
        """
        Rebalance by moving nodes from one side to another.

        Args:
            from_side: List of nodes to move from (modified in place)
            to_side: List of nodes to move to (modified in place)
            locked_node: Node that cannot be moved
            from_height: Current height of the source side
            to_height: Current height of the target side
        """
        # Move oldest nodes first to keep newer nodes stable on their side
        # Use original order: oldest nodes are at the beginning of the list
        # CRITICAL: Also exclude nodes with is_locked_position flag set
        candidates = [
            (node, self._calculate_subtree_height(node))
            for node in from_side
            if node != locked_node and not getattr(node, "is_locked_position", False)
        ]

        for node, height in candidates:
            if from_height <= to_height:
                break
            # Get spacing based on the maximum depth of this node's subtree
            sibling_spacing = self._get_sibling_spacing_for_nodes([node])
            # Try moving this node
            actual_move = height + (sibling_spacing if to_side else 0)
            actual_remove = height + (sibling_spacing if len(from_side) > 1 else 0)

            new_from = from_height - actual_remove
            new_to = to_height + actual_move

            # Only move if it improves balance
            if abs(new_from - new_to) < abs(from_height - to_height):
                from_side.remove(node)
                to_side.append(node)
                from_height = new_from
                to_height = new_to

    def _has_complex_branch(self, nodes: list) -> bool:
        """
        Check if any node in the list has >= 2 children (recursively).

        Args:
            nodes: List of nodes to check

        Returns:
            True if any node has >= 2 children
        """
        for node in nodes:
            if len(node.children) >= 2:
                return True
            # Recursively check children
            if node.children and self._has_complex_branch(node.children):
                return True
        return False

    def _get_root_node(self, node):
        """Get the root node by traversing up the parent chain.

        Args:
            node: Any node in the tree

        Returns:
            The root node, or None if not found
        """
        current = node
        while current and not current.is_root:
            if not current.parent:
                return current
            current = current.parent
        return current

    def _move_branch(self, nodes: list, offset: float) -> None:
        """
        Move an entire branch (including all descendants) by a vertical offset.

        Args:
            nodes: List of nodes to move
            offset: Vertical offset to apply
        """
        for node in nodes:
            x, y = node.position
            node.position = (x, y + offset)
            if node.children:
                self._move_branch(node.children, offset)

    def _get_branch_bounds(self, nodes: list) -> tuple[float, float]:
        """
        Get the top and bottom Y bounds of a branch (including all descendants).

        Args:
            nodes: List of nodes at the top of the branch

        Returns:
            Tuple of (top_y, bottom_y)
        """
        if not nodes:
            return (0.0, 0.0)

        min_y = float("inf")
        max_y = float("-inf")

        for node in nodes:
            # Node's own bounds
            # CRITICAL FIX: position[1] is the CENTER Y coordinate, not the top
            # CRITICAL: Border extends FULL border_width outward from rect (not half!)
            # Visual bounds = rect bounds + border_width on each side
            visual_half_height = self._get_visual_height(node) / 2.0

            node_top = node.position[1] - visual_half_height
            node_bottom = node.position[1] + visual_half_height
            min_y = min(min_y, node_top)
            max_y = max(max_y, node_bottom)

            # Children's bounds
            if node.children:
                child_top, child_bottom = self._get_branch_bounds(node.children)
                min_y = min(min_y, child_top)
                max_y = max(max_y, child_bottom)

        return (min_y, max_y)

    def _layout_side(
        self, nodes: list, parent_node, canvas_height: float, direction: int
    ) -> None:
        """
        Layout one side (left or right) of the tree.

        Default-style: Each node's X position is calculated based on its parent,
        not aligned to a fixed column. This allows short branches to stay compact.

        Implements the three principles:
        1. Simple case: vertical centering when no node has >= 2 children
        2. Complex case: upward expansion when any node has >= 2 children
        3. Recursive avoidance: move all sibling subtrees when overlap occurs

        Args:
            nodes: List of sibling nodes
            parent_node: Parent node of these siblings
            canvas_height: Canvas height for centering
            direction: -1 for left, 1 for right
        """
        if not nodes:
            return

        # Default-style: Calculate X position for each node based on its parent
        # Not a fixed column - each branch extends naturally
        # This will be done in _layout_branch_simple and _layout_branch_complex

        # Check if this is a complex branch (any node has >= 2 children)
        is_complex = self._has_complex_branch(nodes)

        if not is_complex:
            # === Principle 1: Simple case - vertical centering ===
            # All nodes have 0 or 1 child, use simple vertical centering
            # Note: position[1] is already the center Y coordinate
            self._layout_branch_simple(
                nodes,
                parent_node,
                parent_node.position[1],  # position is the center point
                direction,
                canvas_height,
            )
        else:
            # === Principle 2 & 3: Complex case - recursive avoidance ===
            self._layout_branch_complex(nodes, parent_node, direction, canvas_height)

    def _layout_branch_simple(
        self,
        nodes: list,
        parent_node,
        parent_center_y: float,
        direction: int,
        canvas_height: float = 800.0,
    ) -> None:
        """
        Layout a simple branch where no node has >= 2 children.

        Default-style: Each node's X is calculated based on its own parent,
        not a shared column X.

        Args:
            nodes: List of sibling nodes
            parent_node: The parent of these nodes
            parent_center_y: Parent node's center Y coordinate
            direction: -1 for left, 1 for right
            canvas_height: Canvas height for centering
        """
        # Calculate total height of nodes only (not subtrees)
        # CRITICAL: Visual height includes border expansion on both top and bottom
        nodes_height = sum(self._get_visual_height(node) for node in nodes)

        # Rule 1: Sibling spacing must be >= nodes' own level spacing (minimum requirement)
        nodes_level_spacing = self._get_sibling_spacing_for_depth(nodes[0].depth)

        # Rule 2: If nodes have children, spacing between their subtrees
        # uses the deepest level among adjacent subtrees
        # Final spacing = max(rule1_minimum, rule2_subtree_spacing)
        if any(node.children for node in nodes):
            # Find max depth across all subtrees
            max_depth = max(self._get_max_subtree_depth(node) for node in nodes if node.children)
            effective_depth = min(max_depth, 3)
            subtree_spacing = self._get_sibling_spacing_for_depth(effective_depth)
            # Must satisfy BOTH rules: >= nodes' level AND use subtree depth
            sibling_spacing = max(nodes_level_spacing, subtree_spacing)
        else:
            # No children, just use nodes' own level spacing
            sibling_spacing = nodes_level_spacing

        nodes_spacing = (len(nodes) - 1) * sibling_spacing
        total_height = nodes_height + nodes_spacing

        # Calculate the aligned edge position for all sibling nodes
        aligned_edge_x = self._calculate_aligned_edge(parent_node, nodes, direction)

        # Special case: single node should be vertically centered with parent
        if len(nodes) == 1:
            # Single node: center it with parent's center
            node = nodes[0]
            # Calculate node center position using unified method
            node_x = self._calculate_node_position(node, aligned_edge_x, direction)

            # Center the node vertically with parent
            node_y = parent_center_y

            node.position = (node_x, node_y)

            # Layout children if any
            if node.children:
                self._layout_side(node.children, node, canvas_height, direction)

            return

        # Multiple nodes: use the original logic with start_y calculation
        # Start Y for vertical centering
        # CRITICAL FIX: total_height is from top of first node to bottom of last node
        # So we need to add half of first node's height to get its center
        # CRITICAL: Visual height includes border expansion
        if nodes:
            first_node_visual_height = self._get_visual_height(nodes[0])
            start_y = parent_center_y - total_height / 2.0 + first_node_visual_height / 2.0
        else:
            start_y = parent_center_y
        current_y = start_y

        # Calculate the aligned edge position for all sibling nodes
        aligned_edge_x = self._calculate_aligned_edge(parent_node, nodes, direction)

        for node in nodes:
            # Calculate node center position using unified method
            node_x = self._calculate_node_position(node, aligned_edge_x, direction)

            node.position = (node_x, current_y)

            # Layout children if any
            if node.children:
                # Recursively layout children using _layout_side (checks for complex branches)
                # The parent of node.children is 'node', so we pass 'node' directly
                # Rule 4: Left node's children on left, right node's children on right
                # CRITICAL: Compare node's center with ROOT's center, not parent's center!
                # Find root by traversing up the parent chain
                root_node = self._get_root_node(node)
                if root_node:
                    root_center_x = root_node.position[0] + root_node.width / 2
                    node_center_x = node.position[0] + node.width / 2
                    child_direction = 1 if node_center_x >= root_center_x else -1
                else:
                    # Fallback: use parent as reference
                    parent_center_x = (
                        parent_node.position[0] + parent_node.width / 2
                        if parent_node
                        else 0.0
                    )
                    node_center_x = node.position[0] + node.width / 2
                    child_direction = 1 if node_center_x >= parent_center_x else -1
                self._layout_side(node.children, node, canvas_height, child_direction)

            # CRITICAL: Move current_y by visual height (including border expansion)
            current_y += self._get_visual_height(node) + sibling_spacing

    def _layout_branch_complex(
        self, nodes: list, parent_node, direction: int, canvas_height: float
    ) -> None:
        """
        Layout a complex branch where some nodes have >= 2 children.

        Default-style: Each node's X is calculated based on its parent.
        Uses iterative detection and avoidance with TRUE BIDIRECTIONAL expansion:
        1. Start with vertical centering
        2. Detect overlaps from subtrees
        3. Split the overlap evenly: move upper nodes up, lower nodes down

        Args:
            nodes: List of sibling nodes
            parent_node: Parent node of these nodes
            direction: -1 for left, 1 for right
            canvas_height: Canvas height for centering
        """
        # Step 1: Initial vertical centering
        nodes_height = sum(self._get_visual_height(node) for node in nodes)

        # Rule 1: Sibling spacing must be >= nodes' own level spacing (minimum requirement)
        nodes_level_spacing = self._get_sibling_spacing_for_depth(nodes[0].depth)

        # Rule 2: If nodes have children, spacing between their subtrees
        # uses the deepest level among adjacent subtrees
        # Final spacing = max(rule1_minimum, rule2_subtree_spacing)
        if any(node.children for node in nodes):
            # Find max depth across all subtrees
            max_depth = max(self._get_max_subtree_depth(node) for node in nodes if node.children)
            effective_depth = min(max_depth, 3)
            subtree_spacing = self._get_sibling_spacing_for_depth(effective_depth)
            # Must satisfy BOTH rules: >= nodes' level AND use subtree depth
            sibling_spacing = max(nodes_level_spacing, subtree_spacing)
        else:
            # No children, just use nodes' own level spacing
            sibling_spacing = nodes_level_spacing

        nodes_spacing = (len(nodes) - 1) * sibling_spacing
        total_height = nodes_height + nodes_spacing
        # CRITICAL FIX: total_height is from top of first node to bottom of last node
        # So we need to add half of first node's height to get its center
        if nodes:
            start_y = (
                parent_node.position[1] - total_height / 2.0 + self._get_visual_height(nodes[0]) / 2.0
            )
        else:
            start_y = parent_node.position[1]

        # Set initial positions (Default-style: X based on parent)
        current_y = start_y

        # Calculate the aligned edge position for all sibling nodes
        # Use child's depth (parent.depth + 1) for spacing lookup
        level_spacing = self._get_level_spacing_for_depth(parent_node.depth + 1)

        # For left side (direction=-1): align right edge of children
        # For right side (direction=1): align left edge of children
        # Use visual width (including border expansion)
        parent_border = getattr(parent_node, 'border_width', 0)
        parent_visual_width = parent_node.width + parent_border * 2

        if direction == -1:  # Left side
            # Parent's visual left edge
            parent_visual_left = parent_node.position[0] - parent_visual_width / 2.0
            aligned_edge_x = parent_visual_left - level_spacing
        else:  # Right side
            # Parent's visual right edge
            parent_visual_right = parent_node.position[0] + parent_visual_width / 2.0
            aligned_edge_x = parent_visual_right + level_spacing

        for node in nodes:
            # Calculate node center position using unified method
            node_x = self._calculate_node_position(node, aligned_edge_x, direction)

            node.position = (node_x, current_y)
            # CRITICAL: Move current_y by visual height (including border expansion)
            current_y += self._get_visual_height(node) + sibling_spacing

        # Step 2: Layout children and detect overlaps iteratively
        max_iterations = 20
        for _ in range(max_iterations):
            moved = False

            # Layout all children using _layout_side (which checks for complex branches)
            for node in nodes:
                if node.children:
                    # Rule 4: Left node's children on left, right node's children on right
                    # CRITICAL: Compare node's center with ROOT's center, not parent's center!
                    root_node = self._get_root_node(node)
                    if root_node:
                        root_center_x = root_node.position[0] + root_node.width / 2
                        node_center_x = node.position[0] + node.width / 2
                        child_direction = 1 if node_center_x >= root_center_x else -1
                    else:
                        # Fallback: use parent as reference
                        parent_center_x = (
                            parent_node.position[0] + parent_node.width / 2
                            if parent_node
                            else 0.0
                        )
                        node_center_x = node.position[0] + node.width / 2
                        child_direction = 1 if node_center_x >= parent_center_x else -1
                    self._layout_side(
                        node.children, node, canvas_height, child_direction
                    )

            # Check for overlaps between all pairs of sibling subtrees
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    # Get bounds of subtree i
                    top_i, bottom_i = self._get_branch_bounds([nodes[i]])

                    # Get bounds of subtree j
                    top_j, bottom_j = self._get_branch_bounds([nodes[j]])

                    # CRITICAL: Use the maximum depth between the two subtrees for spacing
                    # This ensures we use the appropriate spacing for the deepest level
                    sibling_spacing = self._get_sibling_spacing_for_nodes([nodes[i], nodes[j]])

                    # Check if subtree i overlaps with subtree j
                    if bottom_i + sibling_spacing > top_j:
                        # Overlap detected - SPLIT the movement equally!
                        overlap = bottom_i + sibling_spacing - top_j
                        half_overlap = overlap / 2.0

                        # Move upper nodes (0 to i) UPWARD
                        self._move_branch(nodes[0 : i + 1], -half_overlap)

                        # Move lower nodes (j onwards) DOWNWARD
                        self._move_branch(nodes[j:], half_overlap)

                        moved = True
                        break

                if moved:
                    break

            if not moved:
                break


# Register DefaultLayout in the global registry
layout_registry.register("default", DefaultLayout)
