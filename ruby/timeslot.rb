class Timeslot
  def initialize(x, y, slots_available)
    @x = x
    @y = y
    @slots_available = slots_available
    @players = []
  end

  def full
    @players.length == @slots_available
  end

  def add_player(player)
    @players.push(player)
  end

  def players
    @players
  end

  def x
    @x
  end

  def y
    @y
  end

  def print
    printf "[ %{slots_available} %{players} ]" % {slots_available: @slots_available, players: @players}
  end
end