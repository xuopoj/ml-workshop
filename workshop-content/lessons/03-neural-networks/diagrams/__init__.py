# diagrams - 神经网络可视化模块
# Visualization module for neural network tutorial

from .perceptron import (
    plot_perceptron_boundary,
    plot_xor_problem,
    plot_neuron_diagram,
    plot_perceptron_vs_neuron,
)

from .activations import (
    plot_activation,
    plot_activation_comparison,
    plot_activation_derivatives,
    plot_dying_relu,
)

from .network import (
    plot_network,
    plot_layer_dimensions,
    plot_depth_vs_width,
    plot_feature_hierarchy,
)

from .propagation import (
    plot_forward_pass,
    plot_computational_graph,
    plot_backprop_flow,
    plot_chain_rule_demo,
    plot_batch_dimensions,
)

from .loss import (
    plot_loss_landscape,
    plot_loss_contour,
    plot_gradient_descent_path,
    plot_loss_comparison,
    plot_learning_rate_effect,
)

from .training import (
    # Initialization
    plot_init_distributions,
    plot_activation_histograms,
    # Normalization
    plot_batch_norm_effect,
    plot_internal_covariate_shift,
    plot_norm_comparison,
    # Regularization
    plot_overfitting_curves,
    plot_dropout_network,
    plot_l2_regularization_effect,
    # Optimization
    plot_optimizer_comparison,
    plot_momentum_visualization,
    plot_learning_rate_schedule,
)
