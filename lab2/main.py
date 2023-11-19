from typing import List
from network import Network, Point, Topology
from plotter import Plotter


def main():
    plt = Plotter()

    line_topology_network = Network(
        nodes=[Point(0.0, 0.0), Point(1.0, 1.0), Point(2.0, 2.0), Point(3.0, 3.0), Point(4.0, 4.0), Point(5.0, 5.0)],
        connection_radius=1.5
    )
    line_topology_network.build_graph()
    plt.plot_points(line_topology_network.nodes, True, 'full_line_points')
    plt.plot_network_grapth(line_topology_network, 'full_line')
    line_topology_network.ospf('line_full')

    line_topology_network.remove_node(3)
    plt.plot_network_grapth(line_topology_network, 'rm_line')
    line_topology_network.ospf('line_remove')

    def ring_points(r: float) -> List[Point]:
        xs = [-3.0, -2.7, -2.0, -1.0]
        xs = xs + [0.0] + [-x_k for x_k in xs]
        ys = []
        for x_k in xs:
            y_abs = (r * r - x_k * x_k) ** 0.5;
            ys.extend([y_abs, -y_abs])

        points = []
        for i, x_k in enumerate(xs):
            if ys[2 * i] == 0:
                points.extend([Point(x_k, ys[2 * i])])
            else:
                points.extend([Point(x_k, ys[2 * i]), Point(x_k, ys[2 * i + 1])])
        
        return points
    
    ring_topology_network = Network(
        nodes=ring_points(3.0),
        connection_radius=1.7
    )
    ring_topology_network.build_graph()
    ring_topology_network.ospf('ring_full')
    plt.plot_points(ring_topology_network.nodes, True, 'full_ring_points')
    plt.plot_network_grapth(ring_topology_network, 'full_ring')

    ring_topology_network.remove_node(11)
    ring_topology_network.ospf('ring_remove')
    plt.plot_network_grapth(ring_topology_network, 'rm_ring')

    star_topology_nerwork = Network.create_network(Topology.kStar)
    plt.plot_points(star_topology_nerwork.nodes, True, 'full_star_points')
    plt.plot_network_grapth(star_topology_nerwork, 'full_star')
    star_topology_nerwork.ospf('star_full')

    star_topology_nerwork.remove_node(0)
    plt.plot_network_grapth(star_topology_nerwork, 'rm_star')
    star_topology_nerwork.ospf('star_remove')


if __name__ == '__main__':
    main()
